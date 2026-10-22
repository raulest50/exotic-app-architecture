"""Relational metamodel, with native Gaphor references and UML documentation."""

from gaphor import UML
from gaphor.core.modeling.properties import association, attribute


class boolean(attribute):
    """Gaphor 3.3.2 serializes attributes as strings, including clipboard data."""
    def __init__(self, name, default=False):
        super().__init__(name, bool, default=default)

    def load(self, obj, value):
        if isinstance(value, str):
            if value not in ("True", "False", "1", "0"):
                raise ValueError(f"Invalid boolean: {value!r}")
            value = value in ("True", "1")
        self.set(obj, value)


class PGDatabase(UML.Package):
    formatVersion = attribute("formatVersion", int, default=1)


class PGSchema(UML.Package):
    pass


class PGTable(UML.Class):
    pass


class PGColumn(UML.Property):
    sqlType = attribute("sqlType", str, default="text")
    nullable = boolean("nullable", default=True)
    defaultSql = attribute("defaultSql", str, default="")
    identity = attribute("identity", str, default="NONE")
    position = attribute("position", int, default=0)


class PGKey(UML.Constraint):
    kind = attribute("kind", str, default="UNIQUE")
    nullsNotDistinct = boolean("nullsNotDistinct")


class PGForeignKey(UML.Constraint):
    onDelete = attribute("onDelete", str, default="NO ACTION")
    onUpdate = attribute("onUpdate", str, default="NO ACTION")


class PGColumnPair(UML.Element):
    position = attribute("position", int, default=0)


class PGCheck(UML.Constraint):
    expression = attribute("expression", str, default="")


class PGIndex(UML.Constraint):
    method = attribute("method", str, default="btree")
    unique = boolean("unique")
    nullsNotDistinct = boolean("nullsNotDistinct")
    predicate = attribute("predicate", str, default="")


class PGIndexEntry(UML.Element):
    expression = attribute("expression", str, default="")
    order = attribute("order", str, default="DEFAULT")
    position = attribute("position", int, default=0)


class PGDiagram(UML.Diagram):
    diagramType = attribute("diagramType", str, default="postgres-relational")


PGKey.columns = association("columns", PGColumn)
PGForeignKey.targetTable = association("targetTable", PGTable, upper=1)
PGForeignKey.pairs = association("pairs", PGColumnPair, composite=True, opposite="foreignKey")
PGColumnPair.foreignKey = association("foreignKey", PGForeignKey, upper=1, opposite="pairs")
PGColumnPair.localColumn = association("localColumn", PGColumn, upper=1)
PGColumnPair.remoteColumn = association("remoteColumn", PGColumn, upper=1)
PGIndex.entries = association("entries", PGIndexEntry, composite=True, opposite="index")
PGIndex.includeColumns = association("includeColumns", PGColumn)
PGIndexEntry.index = association("index", PGIndex, upper=1, opposite="entries")
PGIndexEntry.column = association("column", PGColumn, upper=1)
# Native ownership drives the tree, persistence, deep copy and UML documentation.
UML.Element.ownedElement.add(PGForeignKey.pairs)
UML.Element.owner.add(PGColumnPair.foreignKey)
UML.Element.ownedElement.add(PGIndex.entries)
UML.Element.owner.add(PGIndexEntry.index)

MODEL_TYPES = (PGDatabase, PGSchema, PGTable, PGColumn, PGKey, PGForeignKey,
               PGColumnPair, PGCheck, PGIndex, PGIndexEntry, PGDiagram)


def columns(table):
    return sorted((c for c in table.ownedAttribute if isinstance(c, PGColumn)),
                  key=lambda c: (c.position, c.id))


def rules(table, cls=UML.Constraint):
    return [r for r in table.ownedRule if isinstance(r, cls)]


def database(element):
    seen = set()
    while element is not None and element.id not in seen:
        if isinstance(element, PGDatabase):
            return element
        seen.add(element.id)
        element = getattr(element, "owner", None)
    return None


def qualified_name(table):
    return f"{table.package.name}.{table.name}" if table.package else table.name


def key_columns(key):
    if isinstance(key, PGKey):
        return list(key.columns)
    if isinstance(key, PGIndex) and key.unique and not key.predicate:
        entries = sorted(key.entries, key=lambda e: (e.position, e.id))
        if entries and all(e.column is not None and not e.expression for e in entries):
            return [e.column for e in entries]
    return []


def candidate_keys(table):
    return [r for r in rules(table) if key_columns(r)]


def multiplicities(fk):
    """(referenced end, referencing end), derived for MATCH SIMPLE."""
    local = {p.localColumn for p in fk.pairs if p.localColumn}
    optional = any(c.nullable for c in local)
    unique = bool(fk.context and any(set(key_columns(k)) <= local for k in candidate_keys(fk.context)))
    return ("0..1" if optional else "1", "0..1" if unique else "0..*")


def column_label(column):
    table = column.class_
    marks = []
    for key in rules(table, PGKey) if table else []:
        if column in key.columns:
            marks.append("PK" if key.kind == "PRIMARY" else "UQ")
    if table and any(column in key_columns(index) for index in rules(table, PGIndex)):
        marks.append("UQ")
    if table and any(p.localColumn is column for fk in rules(table, PGForeignKey) for p in fk.pairs):
        marks.append("FK")
    if not column.nullable:
        marks.append("NOT NULL")
    return f"{column.name}: {column.sqlType}" + ("  [" + ", ".join(dict.fromkeys(marks)) + "]" if marks else "")


def deletion_dependencies(element):
    """External references that would be broken by deleting this subtree."""
    subtree = set()
    pending = [element]
    while pending:
        current = pending.pop()
        if current in subtree:
            continue
        subtree.add(current)
        pending.extend(getattr(current, "ownedElement", ()))
    result = []
    for rule in element.model.select(lambda e: isinstance(e, (PGKey, PGForeignKey, PGIndex))):
        if rule in subtree:
            continue
        refs = []
        if isinstance(rule, PGKey):
            refs = list(rule.columns)
        elif isinstance(rule, PGForeignKey):
            refs = [rule.targetTable, *(p.localColumn for p in rule.pairs), *(p.remoteColumn for p in rule.pairs)]
            # Removing the only eligible unique key also breaks the FK.
            if rule.targetTable and element in candidate_keys(rule.targetTable):
                target = {p.remoteColumn for p in rule.pairs}
                if not any(k not in subtree and set(key_columns(k)) == target for k in candidate_keys(rule.targetTable)):
                    refs.append(element)
        elif isinstance(rule, PGIndex):
            refs = [*(e.column for e in rule.entries), *rule.includeColumns]
        if any(ref in subtree for ref in refs):
            result.append(rule)
    return result
