"""Editable snapshots and atomic commits. No database connections or SQL execution."""

from copy import deepcopy
from uuid import uuid4

from gaphor.core import Transaction
from .model import (PGDatabase, PGSchema, PGTable, PGColumn, PGKey, PGForeignKey,
                    PGColumnPair, PGCheck, PGIndex, PGIndexEntry, PGDiagram,
                    columns, rules, database)
from .validation import ModelError, identifier, validate


def token():
    return "new:" + str(uuid4())


def new_column():
    return dict(id=token(), name="", type="text", nullable=True, default="", identity="NONE")


def new_key():
    return dict(id=token(), name="", kind="UNIQUE", columns=[], nulls_not_distinct=False)


def new_fk(target=""):
    return dict(id=token(), name="", target=target, pairs=[], on_delete="NO ACTION", on_update="NO ACTION")


def new_check():
    return dict(id=token(), name="", expression="")


def new_index():
    return dict(id=token(), name="", method="btree", unique=False, nulls_not_distinct=False,
                entries=[], include=[], predicate="")


def snapshot(table):
    return dict(id=table.id, name=table.name,
        columns=[dict(id=c.id, name=c.name, type=c.sqlType, nullable=c.nullable,
                      default=c.defaultSql, identity=c.identity) for c in columns(table)],
        keys=[dict(id=k.id, name=k.name, kind=k.kind, columns=[c.id for c in k.columns],
                   nulls_not_distinct=k.nullsNotDistinct) for k in rules(table, PGKey)],
        foreign_keys=[dict(id=f.id, name=f.name, target=f.targetTable.id if f.targetTable else "",
            pairs=[dict(id=p.id, local=p.localColumn.id if p.localColumn else "",
                        remote=p.remoteColumn.id if p.remoteColumn else "")
                   for p in sorted(f.pairs, key=lambda p: (p.position, p.id))],
            on_delete=f.onDelete, on_update=f.onUpdate) for f in rules(table, PGForeignKey)],
        checks=[dict(id=c.id, name=c.name, expression=c.expression) for c in rules(table, PGCheck)],
        indexes=[dict(id=i.id, name=i.name, method=i.method, unique=i.unique,
            nulls_not_distinct=i.nullsNotDistinct, predicate=i.predicate,
            include=[c.id for c in i.includeColumns],
            entries=[dict(id=e.id, column=e.column.id if e.column else "", expression=e.expression, order=e.order)
                     for e in sorted(i.entries, key=lambda e: (e.position, e.id))]) for i in rules(table, PGIndex)])


def database_snapshots(table):
    root = database(table)
    return {t.id: snapshot(t) for t in table.model.select(PGTable) if database(t) is root}


def validate_edit(table, draft):
    if table.model.lookup(table.id) is not table:
        raise ModelError("La tabla ya no existe.")
    if not isinstance(table.package, PGSchema) or database(table) is None:
        raise ModelError("La tabla debe pertenecer a un esquema de una base de datos PostgreSQL.")
    if draft["id"] != table.id:
        raise ModelError("El editor corresponde a otra tabla.")
    for other in table.model.select(PGTable):
        if other is not table and other.package is table.package and other.name == draft["name"]:
            raise ModelError("Ya existe una tabla con ese nombre en el esquema.")
    proposed = database_snapshots(table)
    proposed[table.id] = draft
    root = database(table)
    identifier(root.name, "Base de datos")
    schema_names = set()
    for schema in root.nestedPackage:
        if not isinstance(schema, PGSchema):
            continue
        identifier(schema.name, "Esquema")
        if schema.name in schema_names:
            raise ModelError(f"Esquema repetido: {schema.name}.")
        schema_names.add(schema.name)
        relation_names = set()
        for sibling in table.model.select(PGTable):
            if sibling.package is not schema:
                continue
            state = proposed[sibling.id]
            for name in [state["name"], *(r["name"] for r in state["keys"] + state["indexes"])]:
                if name in relation_names:
                    raise ModelError(f"Nombre de tabla o índice repetido en {schema.name}: {name}.")
                relation_names.add(name)
    warnings = validate(draft, proposed)
    for tid, data in proposed.items():
        if tid != table.id:
            # Checks incoming FKs too: deleting a key/column must not break another table.
            validate(data, proposed)
    return warnings


def _set_many(owner, attr, values):
    collection = getattr(owner, attr)
    for old in list(collection):
        del collection[old]
    for value in values:
        setattr(owner, attr, value)


def save_table(table, draft, events, expected=None):
    draft = deepcopy(draft)
    current = snapshot(table)
    if expected is not None and current != expected:
        raise ModelError("La tabla cambió mientras editabas. Cierra y vuelve a abrir el editor.")
    warnings = validate_edit(table, draft)
    if current == draft:
        return warnings
    old_names = {c["id"]: c["name"] for c in current["columns"]}
    if current["name"] != draft["name"] or any(old_names.get(c["id"], c["name"]) != c["name"] for c in draft["columns"]):
        warnings.append("Nombre actualizado: revisa las expresiones SQL textuales (CHECK, DEFAULT e índices); no se reescriben automáticamente.")
    model = table.model
    owned = {e.id: e for e in [*columns(table), *rules(table)]}
    mapped = {}

    def entity(record, cls, existing):
        rid = record["id"]
        if rid in existing:
            value = existing[rid]
            if type(value) is not cls:
                raise ModelError("El tipo de un elemento cambió.")
        elif rid.startswith("new:"):
            value = model.create(cls)
        else:
            raise ModelError("Un elemento del editor ya no pertenece a la tabla.")
        mapped[rid] = value
        return value

    def column(cid):
        value = mapped.get(cid) or model.lookup(cid)
        if not isinstance(value, PGColumn):
            raise ModelError("Una columna ya no existe.")
        return value

    with Transaction(events):
        table.name = draft["name"]
        for position, rec in enumerate(draft["columns"]):
            col = entity(rec, PGColumn, owned)
            col.class_ = table
            col.name, col.sqlType = rec["name"], rec["type"]
            col.nullable, col.defaultSql, col.identity = rec["nullable"], rec["default"], rec["identity"]
            col.position = position
        for kind, cls in (("keys", PGKey), ("foreign_keys", PGForeignKey), ("checks", PGCheck), ("indexes", PGIndex)):
            for rec in draft[kind]:
                rule = entity(rec, cls, owned)
                rule.context, rule.name = table, rec["name"]
                if cls is PGKey:
                    rule.kind, rule.nullsNotDistinct = rec["kind"], rec["nulls_not_distinct"]
                    _set_many(rule, "columns", [column(cid) for cid in rec["columns"]])
                elif cls is PGCheck:
                    rule.expression = rec["expression"]
                elif cls is PGForeignKey:
                    rule.targetTable = model.lookup(rec["target"])
                    rule.onDelete, rule.onUpdate = rec["on_delete"], rec["on_update"]
                    old_pairs = {p.id: p for p in rule.pairs}
                    keep = set()
                    for position, pair in enumerate(rec["pairs"]):
                        p = entity(pair, PGColumnPair, old_pairs)
                        p.foreignKey, p.position = rule, position
                        p.localColumn, p.remoteColumn = column(pair["local"]), column(pair["remote"])
                        keep.add(p)
                    for p in set(old_pairs.values()) - keep:
                        p.unlink()
                else:
                    rule.method, rule.unique = rec["method"], rec["unique"]
                    rule.nullsNotDistinct, rule.predicate = rec["nulls_not_distinct"], rec["predicate"]
                    _set_many(rule, "includeColumns", [column(cid) for cid in rec["include"]])
                    old_entries = {e.id: e for e in rule.entries}
                    keep = set()
                    for position, entry in enumerate(rec["entries"]):
                        e = entity(entry, PGIndexEntry, old_entries)
                        e.index, e.position = rule, position
                        e.column = column(entry["column"]) if entry["column"] else None
                        e.expression, e.order = entry["expression"], entry["order"]
                        keep.add(e)
                    for e in set(old_entries.values()) - keep:
                        e.unlink()
        keep = set(mapped.values())
        for old in [*rules(table), *columns(table)]:
            if old not in keep:
                old.unlink()
    return warnings


def unique_name(base, elements):
    occupied = {e.name for e in elements}
    name, number = base, 2
    while name in occupied:
        suffix = f"_{number}"
        prefix = base
        while len((prefix + suffix).encode("utf-8")) > 63:
            prefix = prefix[:-1]
        name = prefix + suffix
        number += 1
    return name


def create_database(model, events, name="BaseDatos", parent=None):
    identifier(name, "Base de datos")
    with Transaction(events):
        db = model.create(PGDatabase)
        db.name = unique_name(name, (p for p in model.select(PGDatabase) if p.nestingPackage is parent))
        db.nestingPackage = parent
        schema = model.create(PGSchema)
        schema.name, schema.nestingPackage = "public", db
        diagram = model.create(PGDiagram)
        diagram.name, diagram.element = f"{db.name} — Relacional", db
    return db, schema, diagram
