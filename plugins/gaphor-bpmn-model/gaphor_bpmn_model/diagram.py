"""BPMN presentations and Gaphor's native connection/grouping adapters."""

from dataclasses import replace
from math import cos, pi, sin
from typing import NamedTuple

from gaphas.connector import Handle, LinePort, Position
from gaphas.geometry import Rectangle
from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.diagram.connectors import BaseConnector, Connector
from gaphor.diagram.copypaste import BaseCopy, copy, copy_element, paste, paste_element
from gaphor.diagram.deletable import deletable
from gaphor.diagram.drop import diagram_has_presentation, drop, grow_parent
from gaphor.diagram.group import Root, group, owner, owns, ungroup
from gaphor.diagram.iconname import icon_name
from gaphor.diagram.presentation import ElementPresentation, LinePresentation, Named, connect, text_name
from gaphor.diagram.shapes import CssNode, Text, stroke
from gaphor.diagram.support import represents
from gaphor.event import Notification
from gaphor.UML.general.diagramitem import DiagramItem

from .model import (
    BPMNElement, BPMNCollaboration, BPMNProcess, BPMNParticipant, BPMNLane,
    BPMNFlowNode, BPMNTask, BPMNSubProcess, BPMNEvent, BPMNGateway,
    BPMNSequenceFlow, BPMNMessageFlow, BPMNAssociation, BPMNTextAnnotation,
    BPMNDiagram, can_connect, collaboration, participant, process, scope,
    deletion_dependencies,
)
from .validation import ModelError


FLOW_TYPES = (BPMNSequenceFlow, BPMNMessageFlow, BPMNAssociation)


class BPMNCopyError(ModelError):
    """A paste would lose a BPMN reference or create an ambiguous scope."""


def _copy_error(diagram, message):
    diagram.model.handle(Notification(message))
    raise BPMNCopyError(message)


def _paint(context, *, fill=False, width=None, dash=()):
    style = dict(context.style)
    style["dash-style"] = dash
    if width is not None:
        style["line-width"] = width
    stroke(replace(context, style=style), fill=fill)


def _round_rect(cr, x, y, width, height, radius=10):
    radius = min(radius, width / 2, height / 2)
    cr.new_sub_path()
    for cx, cy, start in ((x + width - radius, y + radius, -pi / 2),
                          (x + width - radius, y + height - radius, 0),
                          (x + radius, y + height - radius, pi / 2),
                          (x + radius, y + radius, pi)):
        cr.arc(cx, cy, radius, start, start + pi / 2)
    cr.close_path()


class BPMNShape:
    """One native shape with a CSS-aware label and an explicit BPMN silhouette."""

    def __init__(self, item):
        self.item = item
        self.label = CssNode("name", item.subject, Text(text=self.label_text))

    def __iter__(self):
        return iter((self.label,))

    def label_text(self):
        value = self.item.subject
        return (value.text if isinstance(value, BPMNTextAnnotation) else value.name) if value else ""

    def size(self, context, bounding_box=None):
        value = self.item.subject
        bounds = bounding_box or Rectangle(0, 0, self.item.width, self.item.height)
        self.label.size(context, Rectangle(0, 0, max(100, bounds.width - 20), bounds.height))
        if isinstance(value, BPMNEvent):
            return 44, 44
        if isinstance(value, BPMNGateway):
            return 54, 54
        if isinstance(value, BPMNParticipant):
            return (260, 80) if value.isClosed else (420, 180)
        if isinstance(value, BPMNLane):
            return 360, 120
        return (160, 80) if isinstance(value, BPMNTextAnnotation) else (140, 76)

    def draw(self, context, bounding_box):
        cr, value = context.cairo, self.item.subject
        x, y, w, h = bounding_box
        if value is None:
            return
        if isinstance(value, BPMNEvent):
            self.draw_event(context, x, y, w, h)
            self.label.draw(context, Rectangle(x - 55, y + h + 6, w + 110, 44))
        elif isinstance(value, BPMNGateway):
            cr.move_to(x + w / 2, y)
            cr.line_to(x + w, y + h / 2)
            cr.line_to(x + w / 2, y + h)
            cr.line_to(x, y + h / 2)
            cr.close_path()
            _paint(context, fill=True)
            cx, cy, r = x + w / 2, y + h / 2, min(w, h) * .15
            if value.gatewayKind == "PARALLEL":
                cr.move_to(cx - r, cy); cr.line_to(cx + r, cy)
                cr.move_to(cx, cy - r); cr.line_to(cx, cy + r)
            else:
                cr.move_to(cx - r, cy - r); cr.line_to(cx + r, cy + r)
                cr.move_to(cx - r, cy + r); cr.line_to(cx + r, cy - r)
            _paint(context, width=3)
            self.label.draw(context, Rectangle(x - 55, y + h + 6, w + 110, 44))
        elif isinstance(value, (BPMNParticipant, BPMNLane)):
            cr.rectangle(x, y, w, h)
            _paint(context, fill=True)
            cr.move_to(x + 32, y); cr.line_to(x + 32, y + h)
            _paint(context)
            cr.save()
            cr.translate(x + 8, y + h - 8)
            cr.rotate(-pi / 2)
            self.label.draw(context, Rectangle(0, 0, h - 16, 22))
            cr.restore()
        elif isinstance(value, BPMNTextAnnotation):
            cr.move_to(x + 12, y); cr.line_to(x, y)
            cr.line_to(x, y + h); cr.line_to(x + 12, y + h)
            _paint(context)
            self.label.draw(context, Rectangle(x + 14, y + 6, w - 20, h - 12))
        else:
            _round_rect(cr, x, y, w, h)
            _paint(context, fill=True)
            marker = isinstance(value, BPMNSubProcess)
            self.label.draw(context, Rectangle(x + 10, y + 10, w - 20, h - (32 if marker else 20)))
            if marker:
                cx, cy = x + w / 2, y + h - 12
                cr.rectangle(cx - 6, cy - 6, 12, 12)
                cr.move_to(cx - 4, cy); cr.line_to(cx + 4, cy)
                cr.move_to(cx, cy - 4); cr.line_to(cx, cy + 4)
                _paint(context, width=1.3)
            if getattr(value, "loopKind", "NONE") == "STANDARD":
                cx, cy = x + w / 2 - (18 if marker else 0), y + h - 12
                cr.arc(cx, cy, 6, -.3, 1.7 * pi)
                cr.line_to(cx + 1, cy - 8)
                _paint(context, width=1.4)

    def draw_event(self, context, x, y, width, height):
        cr, value = context.cairo, self.item.subject
        radius = min(width, height) / 2 - 2
        cx, cy = x + width / 2, y + height / 2
        cr.arc(cx, cy, radius, 0, 2 * pi)
        _paint(context, fill=True, width=3.5 if value.eventKind == "END" else 1.5)
        if value.eventKind == "INTERMEDIATE":
            cr.arc(cx, cy, radius - 4, 0, 2 * pi)
            _paint(context, width=1.2)
        if value.eventDefinition == "MESSAGE":
            r = radius * .48
            cr.rectangle(cx - r, cy - r * .7, 2 * r, 1.4 * r)
            throwing = value.eventKind == "END" or (value.eventKind == "INTERMEDIATE" and value.eventDirection == "THROW")
            if throwing:
                cr.save()
                cr.set_source_rgba(*context.style.get("color", (0, 0, 0, 1)))
                cr.fill_preserve(); cr.restore()
            _paint(context, width=1.2)
            if throwing:
                cr.save()
                color = context.style.get("color", (0, 0, 0, 1))
                cr.set_source_rgb(0, 0, 0) if sum(color[:3]) > 1.5 else cr.set_source_rgb(1, 1, 1)
                cr.move_to(cx - r, cy - r * .7); cr.line_to(cx, cy + .2 * r); cr.line_to(cx + r, cy - r * .7)
                cr.set_line_width(1); cr.stroke(); cr.restore()
            else:
                cr.move_to(cx - r, cy - r * .7); cr.line_to(cx, cy + .2 * r); cr.line_to(cx + r, cy - r * .7)
                _paint(context, width=1)
        elif value.eventDefinition == "TIMER":
            r = radius * .58
            cr.arc(cx, cy, r, 0, 2 * pi)
            cr.move_to(cx, cy - r * .7); cr.line_to(cx, cy); cr.line_to(cx + r * .6, cy + r * .2)
            _paint(context, width=1.2)


class BPMNElementItem(Named, ElementPresentation):
    def __init__(self, diagram, id=None, **kwargs):
        super().__init__(diagram, id=id, **kwargs)
        self.watch("subject[NamedElement].name", self.update_shapes)
        for cls, properties in ((BPMNTextAnnotation, ("text",)),
                                (BPMNEvent, ("eventKind", "eventDefinition", "eventDirection")),
                                (BPMNGateway, ("gatewayKind",)),
                                (BPMNParticipant, ("isClosed",))):
            for property_name in properties:
                self.watch(f"subject[{cls.__name__}].{property_name}", self.update_shapes)

    def update_shapes(self, event=None):
        self.shape = BPMNShape(self)

    def draw(self, context):
        # A Cairo path survives save/restore. In particular arc() would join a
        # previous item's pending move_to with the event's circumference.
        context.cairo.new_path()
        super().draw(context)
        context.cairo.new_path()

    def outline_ports(self, points):
        vertices = [Position(x, y) for x, y in points]
        self._ports = [LinePort(a, b) for a, b in zip(vertices, vertices[1:] + vertices[:1])]


@represents(BPMNParticipant)
class BPMNParticipantItem(BPMNElementItem):
    def __init__(self, diagram, id=None):
        # ElementPresentation uses these values as solver minima, so passing
        # the expanded default would make a closed pool impossible to shrink.
        super().__init__(diagram, id=id, width=260, height=80)


@represents(BPMNLane)
class BPMNLaneItem(BPMNElementItem):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id, width=650, height=140)


@represents(BPMNTask)
class BPMNTaskItem(BPMNElementItem):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id, width=140, height=76)


@represents(BPMNSubProcess)
class BPMNSubProcessItem(BPMNTaskItem):
    pass


@represents(BPMNEvent)
class BPMNEventItem(BPMNElementItem):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id, width=44, height=44)
        for handle in self.handles():
            handle.movable = False
        self.outline_ports([(22 + 20 * cos(-pi / 2 + i * pi / 8), 22 + 20 * sin(-pi / 2 + i * pi / 8)) for i in range(16)])


@represents(BPMNGateway)
class BPMNGatewayItem(BPMNElementItem):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id, width=54, height=54)
        for handle in self.handles():
            handle.movable = False
        self.outline_ports([(27, 0), (54, 27), (27, 54), (0, 27)])


@represents(BPMNTextAnnotation)
class BPMNTextAnnotationItem(BPMNElementItem):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id, width=180, height=80)


class BPMNFlowItem(Named, LinePresentation):
    flow_type = None
    dash = ()

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id)
        self._shape_middle = CssNode("name", None, Text(text=self.flow_label))
        self.watch("subject[NamedElement].name")
        self.watch("subject[BPMNSequenceFlow].flowKind")
        self.watch("subject[BPMNSequenceFlow].conditionExpression")

    def flow_label(self):
        value = self.subject
        if value is None:
            return ""
        return value.name or (value.conditionExpression if isinstance(value, BPMNSequenceFlow) and value.flowKind == "CONDITIONAL" else "")

    def draw(self, context):
        style = dict(context.style)
        style["dash-style"] = self.dash
        context.cairo.new_path()
        super().draw(replace(context, style=style))
        context.cairo.new_path()

    def draw_head(self, context):
        cr = context.cairo
        if self.flow_type is BPMNAssociation:
            cr.move_to(0, 0)
            return
        cr.move_to(13, -5); cr.line_to(0, 0); cr.line_to(13, 5)
        if self.flow_type is BPMNSequenceFlow:
            cr.close_path()
            cr.save()
            cr.set_source_rgba(*context.style.get("color", (0, 0, 0, 1)))
            cr.fill_preserve(); cr.restore()
        _paint(context, width=1.5)
        cr.move_to(0, 0)

    def draw_tail(self, context):
        cr = context.cairo
        cr.line_to(0, 0)
        _paint(context, dash=self.dash)
        if self.flow_type is BPMNMessageFlow:
            cr.arc(4, 0, 4, 0, 2 * pi)
            _paint(context, fill=True, width=1.2)
        elif self.flow_type is BPMNSequenceFlow and self.subject:
            if self.subject.flowKind == "CONDITIONAL" and not isinstance(self.subject.sourceRef, BPMNGateway):
                cr.move_to(0, 0); cr.line_to(7, -5); cr.line_to(14, 0); cr.line_to(7, 5); cr.close_path()
                _paint(context, fill=True, width=1.2)
            elif self.subject.flowKind == "DEFAULT":
                cr.move_to(5, -6); cr.line_to(12, 6)
                _paint(context, width=1.5)
        cr.move_to(0, 0)


@represents(BPMNSequenceFlow)
class BPMNSequenceFlowItem(BPMNFlowItem):
    flow_type = BPMNSequenceFlow


@represents(BPMNMessageFlow)
class BPMNMessageFlowItem(BPMNFlowItem):
    flow_type = BPMNMessageFlow
    dash = (7, 5)


@represents(BPMNAssociation)
class BPMNAssociationItem(BPMNFlowItem):
    flow_type = BPMNAssociation
    dash = (2, 4)


represents(BPMNDiagram)(DiagramItem)


def flow_owner(cls, source, target):
    return scope(source) if cls is BPMNSequenceFlow else (collaboration(source) or collaboration(target))


def compatible_endpoints(cls, source, target, existing=None):
    if not can_connect(cls, source, target):
        return False
    if existing and len(existing.presentation) > 1 and (existing.sourceRef is not source or existing.targetRef is not target):
        return False
    if cls is BPMNSequenceFlow and existing and existing.flowKind != "NORMAL":
        if not isinstance(source, (BPMNTask, BPMNSubProcess)) and not (isinstance(source, BPMNGateway) and source.gatewayKind == "EXCLUSIVE"):
            return False
        if existing.flowKind == "DEFAULT" and any(f is not existing and f.sourceRef is source and f.flowKind == "DEFAULT" for f in source.model.select(BPMNSequenceFlow)):
            return False
    if cls is BPMNMessageFlow:
        for endpoint in (source, target):
            if isinstance(endpoint, BPMNEvent) and endpoint.eventKind != "START" and any(f is not existing and (f.sourceRef is endpoint or f.targetRef is endpoint) for f in endpoint.model.select(BPMNMessageFlow)):
                return False
    return True


@Connector.register(BPMNElementItem, BPMNFlowItem)
class BPMNConnector(BaseConnector):
    def allow(self, handle, port):
        if not super().allow(handle, port):
            return False
        value = self.element.subject
        cls = self.line.flow_type
        if cls is BPMNSequenceFlow:
            if not isinstance(value, BPMNFlowNode):
                return False
            if isinstance(value, BPMNEvent) and ((handle is self.line.head and value.eventKind == "START") or (handle is self.line.tail and value.eventKind == "END")):
                return False
        elif cls is BPMNMessageFlow:
            if not isinstance(value, (BPMNParticipant, BPMNTask, BPMNSubProcess, BPMNEvent)):
                return False
        elif not isinstance(value, (BPMNFlowNode, BPMNTextAnnotation, BPMNParticipant, BPMNLane)):
            return False
        other = self.get_connected(self.line.opposite(handle))
        if other and other.subject:
            source, target = (other.subject, value) if handle is self.line.head else (value, other.subject)
            return compatible_endpoints(cls, source, target, self.line.subject)
        return True

    def connect(self, handle, port):
        if not self.allow(handle, port):
            return False
        source = self.get_connected(self.line.tail)
        target = self.get_connected(self.line.head)
        if source and target and compatible_endpoints(self.line.flow_type, source.subject, target.subject, self.line.subject):
            value = self.line.subject
            if value is None:
                value = self.line.model.create(self.line.flow_type)
                self.line.subject = value
            value.sourceRef, value.targetRef = source.subject, target.subject
            value.container = flow_owner(self.line.flow_type, source.subject, target.subject)
        return True

    def disconnect(self, handle):
        # A detached view must not silently change the relation's other views.
        # Reconnecting reuses this relation; incomplete drawings retain valid
        # model references and can be restored by dragging from the tree.
        pass


def _same_scope_or_new(element, target_scope):
    return target_scope is not None and (element.container is None or element.container is target_scope)


@owner.register(BPMNElement)
def bpmn_owner(element):
    return element.container or (element.folder if isinstance(element, BPMNCollaboration) else None) or Root


@owns.register(BPMNElement)
def bpmn_owns(element):
    return [*element.ownedElements, *element.ownedDiagram]


@deletable.register(BPMNElement)
def bpmn_deletable(element):
    """Protect references before Gaphor's native deletion unlinks subjects."""
    return not deletion_dependencies(element)


_previous_package_deletable = deletable.dispatch(UML.Package)


@deletable.register(UML.Package)
def bpmn_package_deletable(element):
    """Retain the previous guard and protect BPMN references outside a folder."""
    return _previous_package_deletable(element) and not deletion_dependencies(element)


@group.register(UML.Package, BPMNCollaboration)
def group_collaboration_folder(parent, element):
    if parent.model is not element.model:
        return False
    seen, current = set(), parent
    while current is not None and current.id not in seen:
        if current is element:
            return False
        seen.add(current.id)
        current = getattr(current, "owner", None)
    element.folder = parent
    return True


@ungroup.register(UML.Package, BPMNCollaboration)
def ungroup_collaboration_folder(parent, element):
    if element.folder is not parent:
        return False
    element.folder = None
    return True


@group.register(BPMNCollaboration, BPMNParticipant)
@group.register(BPMNCollaboration, BPMNProcess)
def group_collaboration(parent, element):
    if element.container not in (None, parent):
        return False
    element.container = parent
    return True


@group.register(BPMNParticipant, BPMNLane)
def group_lane(parent, lane):
    if parent.isClosed or not _same_scope_or_new(lane, parent.processRef):
        return False
    lane.container = parent.processRef
    return True


@group.register(BPMNProcess, BPMNFlowNode)
@group.register(BPMNProcess, BPMNTextAnnotation)
def group_process(parent, element):
    if not _same_scope_or_new(element, parent):
        return False
    element.container = parent
    if isinstance(element, BPMNFlowNode):
        element.lane = None
    return True


@group.register(BPMNParticipant, BPMNFlowNode)
@group.register(BPMNParticipant, BPMNTextAnnotation)
def group_pool(parent, element):
    return False if parent.isClosed or not parent.processRef else group_process(parent.processRef, element)


@group.register(BPMNLane, BPMNFlowNode)
@group.register(BPMNLane, BPMNTextAnnotation)
def group_lane_element(parent, element):
    target_scope = process(parent)
    if not _same_scope_or_new(element, target_scope):
        return False
    pool = participant(parent)
    if pool and pool.isClosed:
        return False
    element.container = target_scope
    if isinstance(element, BPMNFlowNode):
        element.lane = parent
    return True


@ungroup.register(BPMNElement, BPMNElement)
def retain_semantic_scope(parent, element):
    if isinstance(parent, BPMNLane) and isinstance(element, BPMNFlowNode) and element.lane is parent:
        element.lane = None
    return True


@drop.register(BPMNElementItem, BPMNElementItem)
def drop_existing_on_container(item, parent, x, y):
    if item.diagram is not parent.diagram or item is parent or parent in item.children:
        return None
    if item.parent is parent:
        return item
    # Native drop ungroups first; check semantics before changing either parent.
    if not group(parent.subject, item.subject):
        return None
    old_parent = item.parent
    grow_parent(parent, item)
    item.change_parent(parent)
    if old_parent:
        old_parent.request_update()
    return item


ITEM_TYPES = {
    BPMNParticipant: BPMNParticipantItem, BPMNLane: BPMNLaneItem,
    BPMNTask: BPMNTaskItem, BPMNSubProcess: BPMNSubProcessItem,
    BPMNEvent: BPMNEventItem, BPMNGateway: BPMNGatewayItem,
    BPMNTextAnnotation: BPMNTextAnnotationItem,
    BPMNSequenceFlow: BPMNSequenceFlowItem, BPMNMessageFlow: BPMNMessageFlowItem,
    BPMNAssociation: BPMNAssociationItem,
}


@drop.register(BPMNElement, Diagram)
def drop_element(element, diagram, x, y):
    if isinstance(element, FLOW_TYPES):
        return drop_flow(element, diagram, x, y)
    cls = ITEM_TYPES.get(type(element))
    if cls is None:
        return None
    if existing := diagram_has_presentation(diagram, element):
        return existing
    parent_subject = (getattr(element, "lane", None) or participant(element)) if isinstance(element, (BPMNFlowNode, BPMNTextAnnotation, BPMNLane)) else None
    parent = diagram_has_presentation(diagram, parent_subject)
    item = diagram.create(cls, subject=element, parent=parent)
    if isinstance(element, BPMNParticipant):
        item.width, item.height = (320, 90) if element.isClosed else (700, 320)
    if parent:
        x, y = parent.matrix_i2c.inverse().transform_point(x, y)
    item.matrix.translate(x, y)
    return item


def drop_flow(flow, diagram, x=0, y=0):
    existing = diagram_has_presentation(diagram, flow)
    source = diagram_has_presentation(diagram, flow.sourceRef)
    target = diagram_has_presentation(diagram, flow.targetRef)
    if not source or not target:
        return None
    item = existing or diagram.create(ITEM_TYPES[type(flow)], subject=flow)
    sx, sy = source.matrix_i2c.transform_point(source.width / 2, source.height / 2)
    tx, ty = target.matrix_i2c.transform_point(target.width / 2, target.height / 2)
    if not existing:
        item.head.pos, item.tail.pos = (sx, sy), (tx, ty)
    if source is target and not existing:
        item.insert_handle(1, Handle((sx + source.width, sy - 45)))
        item.insert_handle(2, Handle((sx + source.width, sy + 45)))
    for handle, endpoint in ((item.head, target), (item.tail, source)):
        current = diagram.connections.get_connection(handle)
        if current is None or current.connected is not endpoint:
            connect(item, handle, endpoint)
    return item


class BPMNCopy(NamedTuple):
    element_copy: BaseCopy


@copy.register(BPMNElement)
def copy_bpmn(element):
    yield element.id, BPMNCopy(copy_element(element))
    if isinstance(element, BPMNParticipant) and element.processRef:
        pending, seen = [element.processRef], set()
        while pending:
            dependency = pending.pop()
            if dependency.id not in seen:
                seen.add(dependency.id)
                yield dependency.id, BPMNCopy(copy_element(dependency))
                pending.extend(dependency.ownedElements)


@paste.register(BPMNCopy)
def paste_bpmn(data, diagram, lookup):
    from .language import primary_process
    paster = paste_element(data.element_copy, diagram, lookup)
    element = next(paster)
    yield element
    next(paster, None)
    if isinstance(element, BPMNCollaboration):
        if element.folder is None and isinstance(diagram.element, UML.Package):
            element.folder = diagram.element
        return
    if isinstance(element, FLOW_TYPES):
        if not element.sourceRef or not element.targetRef or not can_connect(type(element), element.sourceRef, element.targetRef):
            _copy_error(diagram, "La copia requiere los extremos BPMN de sus flujos. Copia también sus nodos o el pool completo.")
        element.container = flow_owner(type(element), element.sourceRef, element.targetRef)
    elif element.container is None:
        if isinstance(element, (BPMNParticipant, BPMNProcess)):
            element.container = collaboration(diagram)
        else:
            element.container = primary_process(diagram)
        if element.container is None:
            _copy_error(diagram, "Pega el elemento en un diagrama con un proceso BPMN inequívoco.")
    if isinstance(element, BPMNParticipant) and not element.isClosed and element.processRef is None:
        _copy_error(diagram, "El pool copiado requiere su proceso BPMN.")
    if isinstance(element, BPMNFlowNode) and element.lane and process(element.lane) is not process(element):
        _copy_error(diagram, "La copia contiene un carril de otro proceso.")


@icon_name.register(BPMNElement)
def bpmn_icon(element):
    if isinstance(element, (BPMNCollaboration, BPMNProcess, BPMNParticipant, BPMNLane)):
        return "gaphor-package-symbolic"
    return "gaphor-association-symbolic" if isinstance(element, FLOW_TYPES) else "gaphor-class-symbolic"
