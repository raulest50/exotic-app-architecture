"""Official modeling-language registration, toolbox and tree creation entries."""

from gaphas.item import SE
from gaphor import UML
from gaphor.abc import ModelingLanguage
from gaphor.diagram.diagramtoolbox import DiagramType, ElementCreateInfo, ToolDef, ToolSection, new_item_factory
from gaphor.UML.general.generaltoolbox import general_tools
from gaphor.UML.treemodel import TreeModel

from . import model, diagram
from .model import PGDatabase, PGSchema, PGTable, PGColumn, PGDiagram, database
from .operations import unique_name


def ensure_database(diagram_model):
    root = database(diagram_model.element)
    if root:
        return root
    factory = diagram_model.model
    root = factory.create(PGDatabase)
    root.name = unique_name("BaseDatos", factory.select(PGDatabase))
    if isinstance(diagram_model.element, UML.Package):
        root.nestingPackage = diagram_model.element
    diagram_model.element = root
    return root


def default_schema(root):
    schemas = [p for p in root.nestedPackage if isinstance(p, PGSchema)]
    if schemas:
        return next((s for s in schemas if s.name == "public"), schemas[0])
    schema = root.model.create(PGSchema)
    schema.name, schema.nestingPackage = "public", root
    return schema


def configure_schema(item):
    root = ensure_database(item.diagram)
    item.subject.nestingPackage = root
    item.subject.name = unique_name("schema", root.nestedPackage)


def configure_table(item):
    schema = item.subject.package
    if not isinstance(schema, PGSchema):
        schema = default_schema(ensure_database(item.diagram))
        item.subject.package = schema
    item.subject.name = unique_name("tabla", schema.ownedType)
    item.width = max(item.width, 240)
    item.height = max(item.height, 90)


relational_tools = ToolSection("PostgreSQL", (
    ToolDef("pg-schema", "Esquema", "gaphor-package-symbolic", None,
            new_item_factory(diagram.PGSchemaItem, PGSchema, configure_schema), SE),
    ToolDef("pg-table", "Tabla", "gaphor-class-symbolic", None,
            new_item_factory(diagram.PGTableItem, PGTable, configure_table), SE),
    # Start in the referencing table (tail), finish in the referenced table (head).
    ToolDef("pg-fk", "Clave foránea (origen → destino)", "gaphor-association-symbolic", None,
            new_item_factory(diagram.PGForeignKeyItem), 0),
))


class RelationalDiagramType(DiagramType):
    def create(self, element_factory, element):
        value = super().create(element_factory, element)
        default_schema(ensure_database(value))
        return value


class PostgreSQLLanguage(ModelingLanguage):
    @property
    def name(self):
        return "PostgreSQL"

    @property
    def toolbox_definition(self):
        return (general_tools, relational_tools)

    @property
    def diagram_types(self):
        return (RelationalDiagramType(PGDiagram, "Diagrama relacional", (relational_tools,),
                                      (type(None), UML.Package)),)

    @property
    def element_types(self):
        return (ElementCreateInfo("pg-database", "Base de datos", PGDatabase, (UML.Package,)),
                ElementCreateInfo("pg-schema", "Esquema", PGSchema, (PGDatabase,)),
                ElementCreateInfo("pg-table", "Tabla", PGTable, (PGSchema,)),
                ElementCreateInfo("pg-column", "Columna", PGColumn, (PGTable,)))

    @property
    def model_browser_model(self):
        return TreeModel

    def lookup_element(self, name, ns=None):
        if ns not in (None, "PostgreSQL"):
            return None
        value = getattr(model, name, None) or getattr(diagram, name, None)
        if isinstance(value, type) and value.__module__.startswith("gaphor_postgres_model."):
            return value
        # Watch paths inherited from UML resolve through the item's namespace.
        return getattr(UML, name, None)
