"""Native Gaphor presentations, crow's-foot ends and relational adapters."""

from math import pi
from typing import NamedTuple
from gaphas.connector import Handle

from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.core.format import format
from gaphor.diagram.connectors import Connector, BaseConnector
from gaphor.diagram.copypaste import copy, copy_element, paste, paste_element, BaseCopy
from gaphor.diagram.deletable import deletable
from gaphor.diagram.drop import drop, diagram_has_presentation
from gaphor.diagram.group import group, owner, owns, ungroup
from gaphor.diagram.iconname import icon_name
from gaphor.diagram.presentation import ElementPresentation, LinePresentation, Named, text_name, connect
from gaphor.diagram.shapes import Box, CssNode, Text, draw_border, draw_top_separator
from gaphor.diagram.support import represents
from gaphor.UML.classes.package import PackageItem
from gaphor.UML.general.diagramitem import DiagramItem

from .model import (PGDatabase, PGSchema, PGTable, PGColumn, PGKey, PGForeignKey,
                    PGCheck, PGIndex, PGColumnPair, PGIndexEntry, PGDiagram,
                    columns, column_label, multiplicities, database, deletion_dependencies)
from .validation import ModelError


@represents(PGDatabase)
class PGDatabaseItem(PackageItem):
    pass


@represents(PGSchema)
class PGSchemaItem(PackageItem):
    pass


@represents(PGTable)
class PGTableItem(Named, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id)
        self.watch("subject[Class].name", self.update_shapes).watch(
            "subject[Class].ownedAttribute", self.update_shapes).watch(
            "subject[Class].ownedAttribute.name", self.update_shapes)

    def update_shapes(self, event=None):
        subject = self.subject
        header = CssNode("name", subject, Text(text=lambda: subject.name if subject else "Tabla"))
        rows = [CssNode("attribute", col, Text(text=lambda c=col: column_label(c)))
                for col in columns(subject)] if subject else []
        self.shape = Box(CssNode("compartment", None, Box(header)),
                         CssNode("compartment", None, Box(*rows, draw=draw_top_separator)), draw=draw_border)
        self.request_update()


@represents(PGForeignKey)
class PGForeignKeyItem(Named, LinePresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id, shape_middle=Box(text_name(self)))
        self.watch("subject[Constraint].name")

    def _ending(self, context, cardinality, tail):
        cr = context.cairo
        if tail:
            cr.line_to(22, 0)
        else:
            cr.move_to(22, 0)
        # Maximal multiplicity nearest the entity, minimal multiplicity inward.
        if cardinality.endswith("*"):
            for dy in (-6, 0, 6):
                cr.move_to(0, dy)
                cr.line_to(10, 0)
        else:
            cr.move_to(5, -6)
            cr.line_to(5, 6)
        if cardinality.startswith("0"):
            cr.new_sub_path()
            cr.arc(17, 0, 4, 0, 2 * pi)
        else:
            cr.move_to(14, -6)
            cr.line_to(14, 6)
        cr.move_to(22, 0)

    def draw_head(self, context):
        # Head = referenced table; tail = referencing table.
        self._ending(context, multiplicities(self.subject)[0] if self.subject else "1", False)

    def draw_tail(self, context):
        self._ending(context, multiplicities(self.subject)[1] if self.subject else "0..*", True)


represents(PGDiagram)(DiagramItem)


@Connector.register(PGTableItem, PGForeignKeyItem)
class ForeignKeyConnector(BaseConnector):
    def allow(self, handle, port):
        if not super().allow(handle, port):
            return False
        table = self.element.subject
        if not isinstance(table, PGTable) or not database(table):
            return False
        if fk := self.line.subject:
            # Moving a handle cannot silently change the FK's meaning.
            return table is (fk.targetTable if handle is self.line.head else fk.context)
        other = self.get_connected(self.line.opposite(handle))
        return other is None or database(other.subject) is database(table)


@drop.register(PGForeignKey, Diagram)
def drop_fk(fk, diagram, x, y):
    target = diagram_has_presentation(diagram, fk.targetTable)
    source = diagram_has_presentation(diagram, fk.context)
    if not target or not source:
        return None
    siblings = [i for i in diagram.get_all_items() if isinstance(i, PGForeignKeyItem) and i.subject
                and i.subject.context is fk.context and i.subject.targetTable is fk.targetTable]
    line = diagram.create(PGForeignKeyItem, subject=fk)
    if target is source:
        hx, hy = target.matrix_i2c.transform_point(target.width, target.height / 3)
        tx, ty = target.matrix_i2c.transform_point(target.width, target.height * 2 / 3)
        offset = 60 + len(siblings) * 28
        line.head.pos, line.tail.pos = (hx, hy), (tx, ty)
        line.insert_handle(1, Handle((hx + offset, hy)))
        line.insert_handle(2, Handle((tx + offset, ty)))
    else:
        hx, hy = target.matrix_i2c.transform_point(target.width / 2, target.height / 2)
        tx, ty = source.matrix_i2c.transform_point(source.width / 2, source.height / 2)
        # Aim each endpoint toward the other entity, not at the canvas origin.
        line.head.pos, line.tail.pos = (tx, ty), (hx, hy)
        if siblings:
            line.insert_handle(1, Handle(((hx + tx) / 2, (hy + ty) / 2 + 35 * len(siblings))))
    connect(line, line.head, target)
    connect(line, line.tail, source)
    return line


@group.register(UML.Package, PGSchema)
def group_schema(parent, schema):
    if not isinstance(parent, PGDatabase):
        return False
    if schema.nestingPackage is not None and schema.nestingPackage is not parent:
        return False
    schema.nestingPackage = parent
    return True


@group.register(UML.Package, PGTable)
def group_table(parent, table):
    if not isinstance(parent, PGSchema):
        return False
    if table.package and database(table) is not database(parent):
        return False
    if any(t is not table and t.name == table.name for t in parent.ownedType):
        return False
    table.package = parent
    return True


@group.register(UML.Class, PGColumn)
def group_column(parent, column):
    # Column movement changes key ownership: do it explicitly in the editor.
    if not isinstance(parent, PGTable) or (column.class_ and column.class_ is not parent):
        return False
    column.class_ = parent
    return True


@ungroup.register(UML.Package, PGTable)
@ungroup.register(UML.Package, PGSchema)
def retain_owner_when_unnesting(parent, element):
    # Graphical unnesting must not remove the SQL schema/database ownership.
    return True


@owner.register(PGColumnPair)
@owner.register(PGIndexEntry)
def hidden_detail_owner(element):
    return None


@owns.register(PGForeignKey)
def fk_owned(fk):
    return list(fk.pairs) + list(fk.ownedDiagram)


@copy.register(PGForeignKey)
def copy_fk(fk):
    yield fk.id, RelationalCopy(copy_element(fk))
    for pair in fk.pairs:
        yield from copy_relational(pair)


@copy.register(PGIndex)
def copy_index(index):
    yield index.id, RelationalCopy(copy_element(index))
    for entry in index.entries:
        yield from copy_relational(entry)


@owns.register(PGIndex)
def index_owned(index):
    return list(index.entries) + list(index.ownedDiagram)


class RelationalCopy(NamedTuple):
    element_copy: BaseCopy


@copy.register(PGDatabase)
@copy.register(PGSchema)
@copy.register(PGTable)
@copy.register(PGColumn)
@copy.register(PGKey)
@copy.register(PGCheck)
@copy.register(PGColumnPair)
@copy.register(PGIndexEntry)
def copy_relational(element):
    yield element.id, RelationalCopy(copy_element(element))


@paste.register(RelationalCopy)
def paste_relational(data, diagram, lookup):
    from .operations import unique_name
    paster = paste_element(data.element_copy, diagram, lookup)
    element = next(paster)
    yield element
    next(paster, None)
    # Missing references must abort the entire clipboard transaction rather
    # than silently turn a copied FK/index into an incomplete constraint.
    for name in ("targetTable", "localColumn", "remoteColumn", "column", "columns", "includeColumns"):
        serialized = data.element_copy.data.get(name)
        if serialized:
            refs = [serialized] if serialized[0] == "r" else serialized[1] if serialized[0] == "c" else []
            if any(kind == "r" and lookup(ref) is None for kind, ref in refs):
                raise ModelError("La copia requiere tablas o columnas que no existen en este proyecto. Copia también sus dependencias o la base de datos completa.")
    root = database(diagram.element)
    if isinstance(element, PGSchema) and not isinstance(element.nestingPackage, PGDatabase):
        if root is None:
            raise ModelError("Pega el esquema en un diagrama de una base de datos PostgreSQL.")
        element.nestingPackage = root
    if isinstance(element, PGTable):
        if not isinstance(element.package, PGSchema):
            if root is None:
                raise ModelError("Pega la tabla en un diagrama de una base de datos PostgreSQL.")
            schema = next((s for s in root.nestedPackage if isinstance(s, PGSchema) and s.name == "public"), None)
            if schema is None:
                schema = diagram.model.create(PGSchema)
                schema.name, schema.nestingPackage = "public", root
            element.package = schema
        element.name = unique_name(element.name, (t for t in element.package.ownedType if t is not element))
        # PK/UNIQUE create indexes too: their names share the schema namespace.
        others = [t for t in diagram.model.select(PGTable) if t.package is element.package and t is not element]
        occupied = [*others, *(r for t in others for r in t.ownedRule if isinstance(r, (PGKey, PGIndex)))]
        for rule in element.ownedRule:
            if isinstance(rule, (PGKey, PGIndex)):
                rule.name = unique_name(rule.name, occupied)
                occupied.append(rule)
    elif isinstance(element, (PGDatabase, PGSchema)):
        element.name = unique_name(element.name, (e for e in diagram.model.select(type(element))
                                                 if e is not element and e.nestingPackage is element.nestingPackage))


@deletable.register(PGDatabase)
@deletable.register(PGSchema)
@deletable.register(PGTable)
@deletable.register(PGColumn)
@deletable.register(PGKey)
@deletable.register(PGIndex)
def relational_deletable(element):
    return not deletion_dependencies(element)


@format.register(PGColumn)
def format_column(column, **kwargs):
    return column_label(column)


@icon_name.register(PGDatabase)
@icon_name.register(PGSchema)
def package_icon(element):
    return "gaphor-package-symbolic"


@icon_name.register(PGTable)
def table_icon(element):
    return "gaphor-class-symbolic"


@icon_name.register(PGForeignKey)
def fk_icon(element):
    return "gaphor-association-symbolic"
