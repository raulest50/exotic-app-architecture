import io
import os
from pathlib import Path
from copy import deepcopy
import unittest

from gi.repository import Gtk, GLib
from gaphor import UML
from gaphor.core import Transaction
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import ElementFactory, StyleSheet
from gaphor.core.modeling.elementdispatcher import ElementDispatcher
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.services.undomanager import UndoManager
from gaphor.storage.load import load
from gaphor.storage.save import save
from gaphor.diagram.copypaste import copy_full, paste_full, paste_link
from gaphor.diagram.deletable import deletable
from gaphor.diagram.drop import drop
from gaphor.diagram.export import save_png, save_svg

from gaphor_postgres_model.model import *
from gaphor_postgres_model.operations import *
from gaphor_postgres_model.validation import ModelError
from gaphor_postgres_model.language import PostgreSQLLanguage, relational_tools
from gaphor_postgres_model.diagram import PGTableItem, PGSchemaItem, PGForeignKeyItem, drop_fk


def drain():
    context = GLib.MainContext.default()
    count = 0
    while context.pending() and count < 200:
        context.iteration(False)
        count += 1


class Fixture(unittest.TestCase):
    def setUp(self):
        Gtk.init()
        self.events = EventManager()
        self.language = ModelingLanguageService(self.events)
        self.language._modeling_languages["PostgreSQL"] = PostgreSQLLanguage()
        self.dispatcher = ElementDispatcher(self.events, self.language)
        self.model = ElementFactory(self.events, self.dispatcher)
        self.undo = UndoManager(self.events, self.model)
        self.db, self.schema, self.diagram = create_database(self.model, self.events)
        self.windows = []
        self.services = []

    def tearDown(self):
        for window in self.windows:
            if not window.finished:
                window.cancel()
        for service in self.services:
            service.shutdown()
        drain()
        self.undo.shutdown()
        self.model.shutdown()
        self.dispatcher.shutdown()
        self.language.shutdown()

    def table(self, name="productos", names=("id",), pk=True, schema=None):
        with Transaction(self.events):
            table = self.model.create(PGTable)
            table.name, table.package = name, schema or self.schema
        data = snapshot(table)
        for name in names:
            col = new_column()
            col.update(name=name, type="bigint")
            data["columns"].append(col)
        if pk:
            key = new_key()
            key.update(name=table.name + "_pk", kind="PRIMARY", columns=[c["id"] for c in data["columns"]])
            data["keys"].append(key)
        save_table(table, data, self.events)
        return table

    def fk(self, source, target, local=None, remote=None):
        data = snapshot(source)
        rec = new_fk(target.id)
        rec["name"] = "fk_" + source.name + "_" + target.name
        for left, right in zip(local or columns(source), remote or columns(target)):
            rec["pairs"].append(dict(id=token(), local=left.id, remote=right.id))
        data["foreign_keys"].append(rec)
        save_table(source, data, self.events)
        return rules(source, PGForeignKey)[-1]

    def visual(self, table, x=20, y=50):
        with Transaction(self.events):
            item = self.diagram.create(PGTableItem, subject=table)
            item.matrix.translate(x, y)
            item.width, item.height = 300, 160
        return item


class ModelTests(Fixture):
    def test_language_and_database_defaults(self):
        self.assertEqual(self.schema.name, "public")
        language = self.language._modeling_languages["PostgreSQL"]
        self.assertEqual(language.name, "PostgreSQL")
        self.assertEqual(language.lookup_element("PGTable"), PGTable)
        self.assertEqual(language.diagram_types[0].id, "postgres-relational")

    def test_primary_composite_enforces_not_null(self):
        table = self.table(names=("tenant_id", "id"))
        self.assertTrue(all(not c.nullable for c in columns(table)))
        self.assertEqual(len(rules(table, PGKey)[0].columns), 2)

    def test_table_without_primary_is_supported(self):
        table = self.table(pk=False)
        self.assertEqual(rules(table, PGKey), [])

    def test_unicode_type_parameters_arrays_and_defaults(self):
        table = self.table("catálogo", pk=False)
        data = snapshot(table)
        data["columns"][0].update(name="descripción", type="custom.tipo[]", default="ARRAY[]::custom.tipo[]")
        save_table(table, data, self.events)
        self.assertEqual(columns(table)[0].sqlType, "custom.tipo[]")
        self.assertEqual(columns(table)[0].name, "descripción")

    def test_duplicate_names_rejected_but_other_schema_allowed(self):
        table = self.table()
        other = self.table("other")
        data = snapshot(other); data["name"] = table.name
        with self.assertRaises(ModelError): save_table(other, data, self.events)
        with Transaction(self.events):
            schema = self.model.create(PGSchema)
            schema.nestingPackage, schema.name = self.db, "otro"
        self.table(table.name, schema=schema)

    def test_invalid_columns_do_not_partially_save(self):
        table = self.table(names=("id", "other"))
        before = snapshot(table)
        data = deepcopy(before); data["name"] = "changed"
        data["columns"][1]["name"] = "id"
        with self.assertRaises(ModelError): save_table(table, data, self.events)
        self.assertEqual(snapshot(table), before)

    def test_identity_default_conflict(self):
        table = self.table()
        data = snapshot(table)
        data["columns"][0].update(identity="ALWAYS", default="42")
        with self.assertRaises(ModelError): save_table(table, data, self.events)

    def test_undo_redo_is_one_transaction(self):
        table = self.table()
        before = snapshot(table)
        self.undo.clear_undo_stack()
        data = deepcopy(before); data["name"] = "new_name"
        data["columns"][0]["name"] = "new_id"
        save_table(table, data, self.events)
        after = snapshot(table)
        self.undo.undo_transaction()
        self.assertEqual(snapshot(table), before)
        self.undo.redo_transaction()
        self.assertEqual(snapshot(table), after)

    def test_stale_editor_rejected(self):
        table = self.table()
        old = snapshot(table)
        with Transaction(self.events): table.name = "renamed"
        with self.assertRaises(ModelError): save_table(table, old, self.events, old)

    def test_foreign_key_composite_and_renaming(self):
        parent = self.table("parent", ("tenant", "id"))
        child = self.table("child", ("tenant", "parent_id"), pk=False)
        fk = self.fk(child, parent)
        self.assertEqual(multiplicities(fk), ("0..1", "0..*"))
        data = snapshot(parent); data["columns"][1]["name"] = "renamed"
        save_table(parent, data, self.events)
        self.assertEqual(list(fk.pairs)[1].remoteColumn.name, "renamed")

    def test_one_to_one_and_required_cardinality(self):
        parent = self.table("parent")
        child = self.table("child")
        fk = self.fk(child, parent)
        self.assertEqual(multiplicities(fk), ("1", "0..1"))

    def test_non_unique_foreign_key_target_rejected(self):
        parent = self.table("parent", pk=False)
        child = self.table("child")
        with self.assertRaises(ModelError): self.fk(child, parent)

    def test_incoming_fk_blocks_removing_primary_or_column(self):
        parent = self.table("parent")
        child = self.table("child")
        self.fk(child, parent)
        before = snapshot(parent)
        for field in ("keys", "columns"):
            data = deepcopy(before); data[field] = []
            with self.assertRaises(ModelError): save_table(parent, data, self.events)
        self.assertFalse(deletable(parent))
        self.assertFalse(deletable(columns(parent)[0]))
        self.assertFalse(deletable(rules(parent, PGKey)[0]))
        self.assertTrue(deletable(self.db))

    def test_self_reference_and_two_links(self):
        table = self.table("nodes", ("id", "parent_id"), pk=False)
        data = snapshot(table); key = new_key()
        key.update(name="pk", kind="PRIMARY", columns=[data["columns"][0]["id"]])
        data["keys"].append(key); save_table(table, data, self.events)
        fk = self.fk(table, table, [columns(table)[1]], [columns(table)[0]])
        self.assertIs(fk.targetTable, table)

    def test_unique_index_is_a_foreign_key_candidate(self):
        target = self.table("target", pk=False)
        data = snapshot(target); idx = new_index()
        idx.update(name="uidx", unique=True, entries=[dict(id=token(), column=columns(target)[0].id, expression="", order="DEFAULT")])
        data["indexes"].append(idx); save_table(target, data, self.events)
        self.fk(self.table("child"), target)
        data = snapshot(target); data["indexes"][0]["predicate"] = "id > 0"
        with self.assertRaises(ModelError): save_table(target, data, self.events)

    def test_check_and_expression_index_preserved(self):
        table = self.table()
        data = snapshot(table); check = new_check(); check.update(name="positive", expression="id > 0")
        data["checks"].append(check)
        idx = new_index(); idx.update(name="expr_idx", predicate="id IS NOT NULL",
            entries=[dict(id=token(), column="", expression="(id + 1)", order="DESC")])
        data["indexes"].append(idx); save_table(table, data, self.events)
        self.assertEqual(rules(table, PGIndex)[0].entries[0].expression, "(id + 1)")
        self.assertEqual(rules(table, PGCheck)[0].expression, "id > 0")

    def test_invalid_index_method_options(self):
        table = self.table()
        data = snapshot(table); idx = new_index()
        idx.update(name="bad", unique=True, method="gin", entries=[dict(id=token(),column=columns(table)[0].id,expression="",order="DEFAULT")])
        data["indexes"].append(idx)
        with self.assertRaises(ModelError): save_table(table, data, self.events)

    def test_roundtrip_relational_references_and_views(self):
        parent = self.table("parent")
        child = self.table("child")
        fk = self.fk(child, parent)
        self.visual(parent); self.visual(child, 470, 50)
        with Transaction(self.events): drop_fk(fk, self.diagram, 0, 0)
        stream = io.StringIO(); save(stream, self.model)
        xml = stream.getvalue()
        self.assertIn("modelinglanguage/PostgreSQL", xml)
        other = ElementFactory(self.events, self.dispatcher)
        try:
            load(io.StringIO(xml), other, self.language)
            recovered = other.lookup(child.id)
            self.assertEqual(snapshot(recovered), snapshot(child))
            self.assertIs(rules(recovered, PGForeignKey)[0].targetTable, other.lookup(parent.id))
            line = next(i for i in other.lookup(self.diagram.id).get_all_items() if isinstance(i, PGForeignKeyItem))
            self.assertIsNotNone(line.diagram.connections.get_connection(line.head))
        finally: other.shutdown()

    def test_without_plugin_fails_explicitly(self):
        self.table()
        stream = io.StringIO(); save(stream, self.model)
        language = ModelingLanguageService(self.events)
        # GAPHOR_PLUGIN_PATH extends, rather than replaces, the user directory.
        # Explicitly simulate a loader without this language after installation.
        language._modeling_languages.pop("PostgreSQL", None)
        other = ElementFactory()
        try:
            with self.assertRaises(ValueError): load(io.StringIO(stream.getvalue()), other, language)
        finally:
            other.shutdown(); language.shutdown()

    def test_shallow_and_deep_paste_references(self):
        parent = self.table("parent")
        child = self.table("child")
        self.fk(child, parent)
        a = self.visual(parent); b = self.visual(child, 470, 50)
        copied = copy_full([a, b], self.model.lookup)
        with Transaction(self.events):
            linked = paste_link(copied, self.diagram)
        self.assertEqual({i.subject for i in linked}, {parent, child})
        with Transaction(self.events):
            pasted = paste_full(copied, self.diagram)
        pasted_tables = {i.subject for i in pasted}
        new_child = next(t for t in pasted_tables if rules(t, PGForeignKey))
        new_fk_value = rules(new_child, PGForeignKey)[0]
        self.assertIn(new_fk_value.targetTable, pasted_tables)
        self.assertIsNot(new_fk_value.targetTable, parent)
        self.assertEqual(len(new_fk_value.pairs), 1)
        self.assertIs(new_fk_value.pairs[0].localColumn.class_, new_child)
        self.assertNotEqual(new_child.name, child.name)
        self.assertIs(columns(new_child)[0].nullable, False)
        validate_edit(new_child, snapshot(new_child))

    def test_false_true_flags_roundtrip(self):
        table = self.table(pk=False)
        data = snapshot(table); key = new_key()
        key.update(name="uq", columns=[columns(table)[0].id], nulls_not_distinct=True)
        data["keys"].append(key)
        idx = new_index(); idx.update(name="uidx", unique=True, nulls_not_distinct=False,
            entries=[dict(id=token(), column=columns(table)[0].id, expression="", order="DEFAULT")])
        data["indexes"].append(idx); save_table(table, data, self.events)
        xml = io.StringIO(); save(xml, self.model)
        other = ElementFactory()
        try:
            load(io.StringIO(xml.getvalue()), other, self.language)
            restored = other.lookup(table.id)
            self.assertIs(columns(restored)[0].nullable, True)
            self.assertIs(rules(restored, PGKey)[0].nullsNotDistinct, True)
            self.assertIs(rules(restored, PGIndex)[0].nullsNotDistinct, False)
            self.assertIs(rules(restored, PGIndex)[0].unique, True)
        finally: other.shutdown()

    def test_duplicate_index_names_across_schema_rejected(self):
        first = self.table("first")
        second = self.table("second")
        data = snapshot(second); data["keys"][0]["name"] = rules(first, PGKey)[0].name
        with self.assertRaises(ModelError): save_table(second, data, self.events)

    def test_check_and_index_have_separate_name_namespaces(self):
        table = self.table()
        data = snapshot(table); check = new_check(); check.update(name="same", expression="id > 0")
        idx = new_index(); idx.update(name="same", entries=[dict(id=token(), column=columns(table)[0].id, expression="", order="DEFAULT")])
        data["checks"].append(check); data["indexes"].append(idx)
        save_table(table, data, self.events)
        self.assertEqual(rules(table, PGCheck)[0].name, rules(table, PGIndex)[0].name)

    def test_identifiers_bytes_and_long_expressions(self):
        table = self.table()
        data = snapshot(table); data["name"] = "á" * 32
        with self.assertRaises(ModelError): save_table(table, data, self.events)
        data["name"] = "á" * 31
        check = new_check(); check.update(name="long_check", expression="id > 0 /*" + " SQL " * 2000 + "*/")
        data["checks"].append(check); save_table(table, data, self.events)
        self.assertEqual(rules(table, PGCheck)[0].expression, check["expression"])
        self.assertLessEqual(len(unique_name(table.name, [table]).encode("utf-8")), 63)

    def test_cross_schema_and_multiple_foreign_keys(self):
        parent = self.table("parent")
        with Transaction(self.events):
            other = self.model.create(PGSchema); other.name = "otros"; other.nestingPackage = self.db
        child = self.table("child", ("id", "ref"), pk=False, schema=other)
        self.fk(child, parent, [columns(child)[0]], [columns(parent)[0]])
        data = snapshot(child); fk = new_fk(parent.id)
        fk.update(name="other_fk", on_delete="CASCADE", on_update="RESTRICT",
                  pairs=[dict(id=token(), local=columns(child)[1].id, remote=columns(parent)[0].id)])
        data["foreign_keys"].append(fk); save_table(child, data, self.events)
        self.assertEqual(len(rules(child, PGForeignKey)), 2)
        self.assertIs(rules(child, PGForeignKey)[1].targetTable.package, self.schema)

    def test_cardinality_composite_nullable_and_unique_subset(self):
        parent = self.table("parent", ("a", "b"))
        child = self.table("child", ("a", "b"), pk=False)
        fk = self.fk(child, parent)
        self.assertEqual(multiplicities(fk), ("0..1", "0..*"))
        data = snapshot(child); data["columns"][0]["nullable"] = False
        key = new_key(); key.update(name="uq", columns=[columns(child)[0].id])
        data["keys"].append(key); save_table(child, data, self.events)
        self.assertEqual(multiplicities(fk), ("0..1", "0..1"))

    def test_bad_foreign_keys_and_type_warnings(self):
        parent = self.table("parent")
        child = self.table("child", pk=False)
        fk = self.fk(child, parent)
        data = snapshot(child); data["columns"][0]["type"] = "uuid"
        self.assertTrue(save_table(child, data, self.events))
        data = snapshot(child); data["foreign_keys"][0]["on_delete"] = "UNKNOWN"
        with self.assertRaises(ModelError): save_table(child, data, self.events)
        data["foreign_keys"][0]["on_delete"] = "NO ACTION"
        data["foreign_keys"][0]["pairs"][0]["remote"] = columns(child)[0].id
        with self.assertRaises(ModelError): save_table(child, data, self.events)

    def test_partial_index_and_include_validation(self):
        table = self.table(names=("id", "payload"))
        data = snapshot(table); idx = new_index()
        idx.update(name="cover", entries=[dict(id=token(),column=columns(table)[0].id,expression="",order="ASC")],
                   include=[columns(table)[1].id], predicate="id > 0")
        data["indexes"].append(idx); save_table(table, data, self.events)
        self.assertIs(rules(table, PGIndex)[0].includeColumns[0], columns(table)[1])
        data = snapshot(table); data["indexes"][0]["include"] = [columns(table)[0].id]
        with self.assertRaises(ModelError): save_table(table, data, self.events)

    def test_graphical_unparent_preserves_schema(self):
        from gaphor.diagram.group import ungroup, group
        table = self.table()
        self.assertTrue(ungroup(self.schema, table))
        self.assertIs(table.package, self.schema)
        db, schema, _ = create_database(self.model, self.events, name="second")
        self.assertFalse(group(schema, table))

    def test_self_relationship_has_visible_loop(self):
        table = self.table("nodes")
        fk = self.fk(table, table)
        self.visual(table)
        with Transaction(self.events):
            line = drop_fk(fk, self.diagram, 0, 0)
            self.diagram.update()
        self.assertEqual(len(line.handles()), 4)
        self.assertGreater(abs(float(line.handles()[1].pos.x) - float(line.head.pos.x)), 30)

    def test_deep_copy_index_entries_and_self_fk(self):
        table = self.table("nodes")
        self.fk(table, table)
        data = snapshot(table); idx = new_index()
        idx.update(name="idx", entries=[dict(id=token(),column=columns(table)[0].id,expression="",order="DESC")])
        data["indexes"].append(idx); save_table(table, data, self.events)
        copied = copy_full([self.visual(table)], self.model.lookup)
        with Transaction(self.events): pasted = paste_full(copied, self.diagram)
        new_table = next(iter(pasted)).subject
        self.assertIs(rules(new_table, PGForeignKey)[0].targetTable, new_table)
        self.assertIs(rules(new_table, PGIndex)[0].entries[0].column.class_, new_table)
        validate_edit(new_table, snapshot(new_table))

    def test_missing_copy_dependency_rolls_back(self):
        parent = self.table("parent"); child = self.table("child")
        self.fk(child, parent)
        copied = copy_full([self.visual(child)], self.model.lookup)
        other_events = EventManager()
        other = ElementFactory(other_events, self.dispatcher)
        manager = UndoManager(other_events, other)
        try:
            _, _, target = create_database(other, other_events)
            before = other.size()
            with self.assertRaises(ModelError):
                with Transaction(other_events): paste_full(copied, target)
            self.assertEqual(other.size(), before)
        finally: manager.shutdown(); other.shutdown()

    def test_copy_complete_database_to_another_model(self):
        from gaphor_postgres_model.diagram import PGDatabaseItem
        parent = self.table("parent"); child = self.table("child")
        self.fk(child, parent)
        with Transaction(self.events): item = self.diagram.create(PGDatabaseItem, subject=self.db)
        copied = copy_full([item], self.model.lookup)
        other_events = EventManager(); other = ElementFactory(other_events, self.dispatcher)
        manager = UndoManager(other_events, other)
        try:
            _, _, target = create_database(other, other_events)
            with Transaction(other_events): pasted = paste_full(copied, target)
            clone = next(i.subject for i in pasted if isinstance(i.subject, PGDatabase))
            tables = [t for t in other.select(PGTable) if database(t) is clone]
            self.assertEqual(len(tables), 2)
            fk = next(r for t in tables for r in rules(t, PGForeignKey))
            self.assertIn(fk.targetTable, tables)
            self.assertIs(fk.pairs[0].localColumn.class_, fk.context)
        finally: manager.shutdown(); other.shutdown()

    def test_native_drop_and_export(self):
        table = self.table("Productos", ("identificador", "categoría"))
        with Transaction(self.events): item = drop(table, self.diagram, 40, 60)
        self.assertIsInstance(item, PGTableItem)
        output = Path(os.environ["GAPHOR_POSTGRES_TEST_OUTPUT"])
        with Transaction(self.events):
            save_png(str(output / "relational.png"), self.diagram)
            save_svg(str(output / "relational.svg"), self.diagram)
        self.assertGreater((output / "relational.png").stat().st_size, 100)
