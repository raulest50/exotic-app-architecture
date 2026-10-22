from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

from gi.repository import Gio, Gtk
from gaphor.core import Transaction
from gaphor.core.modeling.event import ModelReady
from gaphor.diagram.event import DiagramSelectionChanged

from test_model import Fixture, drain
from gaphor_postgres_model.editor import TableEditor, OrderedColumns, Rows
from gaphor_postgres_model.service import PostgresService, selected_table, RelationalPropertyPage
from gaphor_postgres_model.operations import *
from gaphor_postgres_model.model import *


class EditorTests(Fixture):
    def editor(self, table, **kwargs):
        value = TableEditor(None, table, self.events, lambda w: None, **kwargs)
        self.windows.append(value)
        return value

    def test_four_tabs_and_resizable(self):
        editor = self.editor(self.table())
        self.assertEqual(editor.tabs.get_n_pages(), 4)
        self.assertTrue(editor.get_resizable())
        self.assertEqual([editor.tabs.get_tab_label_text(editor.tabs.get_nth_page(n)) for n in range(4)],
                         ["Columnas", "Claves y relaciones", "Restricciones", "Índices"])

    def test_cancel_preserves_model_after_child_saved(self):
        table = self.table(); before = snapshot(table)
        editor = self.editor(table)
        editor.name.set_text("changed")
        editor.lists["columns"].edit(editor.draft["columns"][0])
        child = editor.child
        child.name.set_text("renamed")
        self.assertTrue(child.save())
        self.assertEqual(snapshot(table), before)
        editor.cancel()
        self.assertEqual(snapshot(table), before)

    def test_invalid_draft_stays_open_and_atomic(self):
        table = self.table(); before = snapshot(table)
        editor = self.editor(table)
        editor.name.set_text("changed")
        editor.draft["columns"][0]["type"] = ""
        self.assertFalse(editor.save())
        self.assertFalse(editor.finished)
        self.assertTrue(editor.error.get_text())
        self.assertEqual(snapshot(table), before)

    def test_save_and_undo_with_child_column(self):
        table = self.table(); before = snapshot(table)
        editor = self.editor(table)
        editor.lists["columns"].add()
        editor.child.name.set_text("descripción")
        editor.child.type.get_child().set_text("varchar(2048)[]")
        self.assertTrue(editor.child.save())
        self.undo.clear_undo_stack()
        self.assertTrue(editor.save())
        self.assertTrue(editor.finished)
        self.assertEqual(len(columns(table)), 2)
        self.undo.undo_transaction()
        self.assertEqual(snapshot(table), before)
        self.undo.redo_transaction()
        self.assertEqual(len(columns(table)), 2)

    def test_save_callback_failure_rolls_back(self):
        table = self.table(); before = snapshot(table)
        def fail(_table):
            raise ValueError("callback failed")
        editor = self.editor(table, after_save=fail)
        editor.name.set_text("changed")
        self.assertFalse(editor.save())
        self.assertEqual(snapshot(table), before)
        self.assertFalse(editor.finished)

    def test_target_and_column_selectors_use_ids(self):
        parent = self.table("parent")
        child = self.table("child", pk=False)
        editor = self.editor(child)
        record = new_fk(parent.id); record["name"] = "fk_parent"
        editor.lists["foreign_keys"].edit(record, True)
        form = editor.child
        form.pairs.add()
        _, _, local, remote, _ = form.pairs.controls[0]
        local.set_active_id(columns(child)[0].id)
        remote.set_active_id(columns(parent)[0].id)
        self.assertTrue(form.save())
        self.assertTrue(editor.save())
        self.assertIs(rules(child, PGForeignKey)[0].pairs[0].remoteColumn, columns(parent)[0])

    def test_key_check_and_index_editors(self):
        table = self.table(pk=False)
        editor = self.editor(table)
        for kind, name in (("keys", "unique_id"), ("checks", "positive"), ("indexes", "id_idx")):
            editor.lists[kind].add()
            child = editor.child
            child.name.set_text(name)
            if kind == "keys":
                child.columns.selector.set_active_id(columns(table)[0].id)
                child.columns.add()
                child.nulls.set_active(True)
            elif kind == "checks":
                child.read_expression = lambda: "id > 0"
            else:
                child.entries.add()
                child.entries.controls[0][2].set_active_id(columns(table)[0].id)
                child.entries.controls[0][4].set_active_id("DESC")
                child.read_predicate = lambda: "id IS NOT NULL"
            self.assertTrue(child.save())
        self.assertTrue(editor.save())
        self.assertTrue(rules(table, PGKey)[0].nullsNotDistinct)
        self.assertEqual(rules(table, PGIndex)[0].entries[0].order, "DESC")

    def test_deletion_while_editor_open_keeps_text(self):
        table = self.table(); editor = self.editor(table)
        with Transaction(self.events): table.unlink()
        editor.name.set_text("preserved")
        self.assertFalse(editor.save())
        self.assertEqual(editor.name.get_text(), "preserved")

    def test_ordered_columns_and_entries_reorder(self):
        widget = OrderedColumns([("a", "A"), ("b", "B")], ["a", "b"])
        widget.move(1, -1)
        self.assertEqual(widget.selected, ["b", "a"])
        widget.remove_at(1)
        self.assertEqual(widget.selected, ["b"])
        rows = Rows([], [("a", "A")]); rows.add(); rows.add()
        first = rows.controls[0][0]; second = rows.controls[1][0]
        rows.move(rows.controls[1], -1)
        self.assertEqual([r["id"] for r in rows.read()], [second, first])

    def test_service_selection_uses_real_event(self):
        service = PostgresService(SimpleNamespace(window=None), SimpleNamespace(menu=Gio.Menu()),
                                  self.events, self.model, SimpleNamespace(get_current_diagram=lambda: self.diagram))
        self.services.append(service)
        table = self.table(); item = self.visual(table)
        view = SimpleNamespace(model=self.diagram)
        service._selection(DiagramSelectionChanged(view, None, []))
        self.assertIs(service.focused, self.diagram)
        service._selection(DiagramSelectionChanged(view, item, [item]))
        self.assertIs(selected_table(service.focused), table)
        service._selection(DiagramSelectionChanged(None, None, []))
        self.assertIsNone(service.focused)
        self.assertIsNotNone(RelationalPropertyPage(table, self.events).construct())
        service.open_table(table)
        self.assertIsNotNone(service.window)
        service._reset(ModelReady(self.model))
        self.assertIsNone(service.window)
