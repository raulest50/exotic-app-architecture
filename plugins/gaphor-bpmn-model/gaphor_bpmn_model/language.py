"""BPMN language registration, toolbox factories and native diagram creation."""

from importlib.resources import files

from gaphas.item import SE
from gi.repository import Gdk, Gtk
from gaphor import UML
from gaphor.abc import ModelingLanguage
from gaphor.diagram.diagramtoolbox import DiagramType, ElementCreateInfo, ToolDef, ToolSection, new_item_factory
from gaphor.diagram.group import group
from gaphor.UML.general.generaltoolbox import general_tools
from gaphor.UML.treemodel import TreeModel

from . import model, diagram
from .model import (
    BPMNElement, BPMNCollaboration, BPMNProcess, BPMNParticipant, BPMNLane,
    BPMNTask, BPMNSubProcess, BPMNEvent, BPMNGateway, BPMNTextAnnotation,
    BPMNDiagram, collaboration, process,
)


def ensure_collaboration(diagram_model):
    root = collaboration(diagram_model)
    if root:
        return root
    root = diagram_model.model.create(BPMNCollaboration)
    root.name = "Colaboración"
    if isinstance(diagram_model.element, BPMNProcess):
        diagram_model.element.container = root
    elif isinstance(diagram_model.element, UML.Package):
        root.folder = diagram_model.element
    else:
        diagram_model.element = root
    diagram_model.bpmnCollaboration = root
    return root


def primary_process(diagram_model):
    """Resolve a unique open process; never pick one of several pools by order."""
    if isinstance(diagram_model.element, BPMNProcess):
        return diagram_model.element
    root = collaboration(diagram_model)
    if root is None:
        return None
    pools = [p for p in root.ownedElements if isinstance(p, BPMNParticipant)]
    opened = [p.processRef for p in pools if not p.isClosed and p.processRef]
    if len(opened) == 1:
        return opened[0]
    if pools:
        return None
    processes = [p for p in root.ownedElements if isinstance(p, BPMNProcess)]
    return processes[0] if len(processes) == 1 else None


def _new_pool(diagram_model, closed=False):
    root = ensure_collaboration(diagram_model)
    factory = diagram_model.model
    subject = factory.create(BPMNParticipant)
    subject.name, subject.container, subject.isClosed = "Participante", root, closed
    proc = factory.create(BPMNProcess)
    proc.name, proc.container = "Proceso", root
    subject.processRef = proc
    item = diagram_model.create(diagram.BPMNParticipantItem, subject=subject)
    item.width, item.height = (320, 90) if closed else (700, 320)
    return item


def pool_factory(closed=False):
    def create(diagram_model, parent=None):
        return _new_pool(diagram_model, closed)
    create.item_class = diagram.BPMNParticipantItem
    create.subject_class = BPMNParticipant
    return create


def _context(diagram_model, parent):
    if parent:
        subject = parent.subject
        if isinstance(subject, BPMNParticipant):
            return None if subject.isClosed else subject.processRef
        if isinstance(subject, BPMNLane):
            return process(subject)
        return None
    return primary_process(diagram_model)


def element_factory(cls, item_cls, name, **attributes):
    def create(diagram_model, parent=None):
        subject = diagram_model.model.create(cls)
        subject.name = name
        for attribute, value in attributes.items():
            setattr(subject, attribute, value)
        item = diagram_model.create(item_cls, subject=subject)
        if cls is BPMNTextAnnotation and parent is None:
            subject.container = ensure_collaboration(diagram_model)
            return item
        target = _context(diagram_model, parent)
        if target is None:
            item._bpmn_placement_error = "Dibuja dentro de un pool abierto o un carril; fuera de ellos debe existir un único proceso abierto."
            return item
        subject.container = target
        if parent and group(parent.subject, subject):
            item.change_parent(parent)
        return item
    create.item_class = item_cls
    create.subject_class = cls
    return create


def gateway_factory(is_marker_visible=True):
    factory = element_factory(BPMNGateway, diagram.BPMNGatewayItem, "", gatewayKind="EXCLUSIVE")

    def create(diagram_model, parent=None):
        item = factory(diagram_model, parent)
        item.isMarkerVisible = is_marker_visible
        return item

    create.item_class = factory.item_class
    create.subject_class = factory.subject_class
    return create


def lane_factory(diagram_model, parent=None):
    lane = diagram_model.model.create(BPMNLane)
    lane.name = "Carril"
    item = diagram_model.create(diagram.BPMNLaneItem, subject=lane)
    if parent and not isinstance(parent.subject, BPMNParticipant):
        item._bpmn_placement_error = "Los carriles se dibujan dentro de un pool abierto; no se admiten carriles anidados."
        return item
    target = _context(diagram_model, parent)
    if target is None:
        item._bpmn_placement_error = "Dibuja el carril dentro de un pool abierto."
        return item
    lane.container = target
    if parent:
        item.width = max(360, parent.width - 48)
        item.change_parent(parent)
    return item


lane_factory.item_class = diagram.BPMNLaneItem
lane_factory.subject_class = BPMNLane


def register_icons():
    """Extend the display's icon theme once, using Gaphor's native layout."""
    display = Gdk.Display.get_default()
    if display is None:
        return
    theme = Gtk.IconTheme.get_for_display(display)
    path = str(files("gaphor_bpmn_model") / "icons")
    if path not in theme.get_search_path():
        theme.add_search_path(path)


bpmn_tools = ToolSection("BPMN", (
    ToolDef("bpmn-pool", "Pool abierto", "exotic-bpmn-pool-symbolic", None, pool_factory(), SE),
    ToolDef("bpmn-pool-closed", "Pool cerrado", "exotic-bpmn-pool-closed-symbolic", None, pool_factory(True), SE),
    ToolDef("bpmn-lane", "Carril", "exotic-bpmn-lane-symbolic", None, lane_factory, SE),
    ToolDef("bpmn-task", "Tarea", "exotic-bpmn-task-symbolic", None, element_factory(BPMNTask, diagram.BPMNTaskItem, "Tarea"), SE),
    ToolDef("bpmn-subprocess", "Subproceso colapsado", "exotic-bpmn-subprocess-symbolic", None, element_factory(BPMNSubProcess, diagram.BPMNSubProcessItem, "Subproceso"), SE),
    ToolDef("bpmn-start", "Evento de inicio", "exotic-bpmn-start-symbolic", None, element_factory(BPMNEvent, diagram.BPMNEventItem, "Inicio", eventKind="START", eventDefinition="NONE", eventDirection="CATCH"), -1),
    ToolDef("bpmn-intermediate", "Evento intermedio", "exotic-bpmn-intermediate-symbolic", None, element_factory(BPMNEvent, diagram.BPMNEventItem, "Evento", eventKind="INTERMEDIATE", eventDefinition="NONE", eventDirection="THROW"), -1),
    ToolDef("bpmn-end", "Evento de fin", "exotic-bpmn-end-symbolic", None, element_factory(BPMNEvent, diagram.BPMNEventItem, "Fin", eventKind="END", eventDefinition="NONE", eventDirection="THROW"), -1),
    ToolDef("bpmn-exclusive", "Compuerta exclusiva con X", "exotic-bpmn-exclusive-symbolic", None, gateway_factory(), -1),
    ToolDef("bpmn-exclusive-unmarked", "Compuerta exclusiva sin marcador", "exotic-bpmn-exclusive-unmarked-symbolic", None, gateway_factory(False), -1),
    ToolDef("bpmn-parallel", "Compuerta paralela", "exotic-bpmn-parallel-symbolic", None, element_factory(BPMNGateway, diagram.BPMNGatewayItem, "", gatewayKind="PARALLEL"), -1),
    ToolDef("bpmn-sequence", "Flujo de secuencia (origen → destino)", "exotic-bpmn-sequence-symbolic", None, new_item_factory(diagram.BPMNSequenceFlowItem), 0),
    ToolDef("bpmn-message", "Flujo de mensaje (origen → destino)", "exotic-bpmn-message-symbolic", None, new_item_factory(diagram.BPMNMessageFlowItem), 0),
    ToolDef("bpmn-association", "Asociación de anotación", "exotic-bpmn-association-symbolic", None, new_item_factory(diagram.BPMNAssociationItem), 0),
    ToolDef("bpmn-annotation", "Anotación de texto", "exotic-bpmn-annotation-symbolic", None, element_factory(BPMNTextAnnotation, diagram.BPMNTextAnnotationItem, "", text="Anotación"), SE),
))


class BPMNDiagramType(DiagramType):
    def create(self, element_factory, element):
        value = super().create(element_factory, element)
        root = ensure_collaboration(value)
        value.bpmnCollaboration = root
        if isinstance(element, BPMNProcess):
            return value
        if not any(isinstance(p, BPMNParticipant) for p in root.ownedElements):
            item = _new_pool(value)
            item.matrix.translate(30, 30)
        return value


class BPMNLanguage(ModelingLanguage):
    @property
    def name(self):
        return "BPMN"

    @property
    def toolbox_definition(self):
        register_icons()
        return (general_tools, bpmn_tools)

    @property
    def diagram_types(self):
        return (BPMNDiagramType(BPMNDiagram, "Diagrama BPMN", (bpmn_tools,), (type(None), UML.Package, BPMNCollaboration, BPMNProcess)),)

    @property
    def element_types(self):
        return (ElementCreateInfo("bpmn-collaboration", "Colaboración BPMN", BPMNCollaboration, ()),)

    @property
    def model_browser_model(self):
        return TreeModel

    def lookup_element(self, name, ns=None):
        if ns not in (None, "BPMN"):
            return None
        value = getattr(model, name, None) or getattr(diagram, name, None)
        if isinstance(value, type) and value.__module__.startswith("gaphor_bpmn_model."):
            return value
        # Inherited UML paths are resolved through the item's own namespace.
        return getattr(UML, name, None)
