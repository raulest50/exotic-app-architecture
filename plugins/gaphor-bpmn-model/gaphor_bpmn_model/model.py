"""Persistent BPMN subset, using Gaphor references and composite ownership.

``container`` determines semantic ownership. A lane is an additional assignment;
it never replaces the process or subprocess that owns a flow node.
"""

from gaphor import UML
from gaphor.core.modeling.properties import association, attribute


class boolean(attribute):
    """Load serialized booleans without treating the string 'False' as true."""

    def __init__(self, name, default=False):
        super().__init__(name, bool, default=default)

    def load(self, obj, value):
        if isinstance(value, str):
            if value not in ("True", "False", "1", "0"):
                raise ValueError(f"Invalid boolean: {value!r}")
            value = value in ("True", "1")
        self.set(obj, value)


class BPMNElement(UML.NamedElement):
    documentation = attribute("documentation", str, default="")


class BPMNCollaboration(BPMNElement):
    formatVersion = attribute("formatVersion", int, default=1)


class BPMNProcess(BPMNElement):
    pass


class BPMNParticipant(BPMNElement):
    isClosed = boolean("isClosed")


class BPMNLane(BPMNElement):
    pass


class BPMNFlowNode(BPMNElement):
    pass


class BPMNTask(BPMNFlowNode):
    pass


class BPMNSubProcess(BPMNFlowNode):
    """Collapsed subprocess; its internal scope remains persistable."""


class BPMNEvent(BPMNFlowNode):
    eventKind = attribute("eventKind", str, default="START")
    eventDefinition = attribute("eventDefinition", str, default="NONE")
    eventDirection = attribute("eventDirection", str, default="CATCH")


class BPMNGateway(BPMNFlowNode):
    gatewayKind = attribute("gatewayKind", str, default="EXCLUSIVE")


class BPMNFlow(BPMNElement):
    pass


class BPMNSequenceFlow(BPMNFlow):
    flowKind = attribute("flowKind", str, default="NORMAL")
    conditionExpression = attribute("conditionExpression", str, default="")


class BPMNMessageFlow(BPMNFlow):
    pass


class BPMNAssociation(BPMNFlow):
    pass


class BPMNTextAnnotation(BPMNElement):
    text = attribute("text", str, default="")


class BPMNDiagram(UML.Diagram):
    diagramType = attribute("diagramType", str, default="bpmn")


BPMNElement.container = association("container", BPMNElement, upper=1, opposite="ownedElements")
BPMNElement.ownedElements = association("ownedElements", BPMNElement, composite=True, opposite="container")
BPMNParticipant.processRef = association("processRef", BPMNProcess, upper=1)
BPMNFlowNode.lane = association("lane", BPMNLane, upper=1)
BPMNFlow.sourceRef = association("sourceRef", BPMNElement, upper=1)
BPMNFlow.targetRef = association("targetRef", BPMNElement, upper=1)
# Organization is independent of the BPMN semantic container. Only a
# collaboration can be filed in a UML package; its processes keep their scope.
BPMNCollaboration.folder = association("folder", UML.Package, upper=1, opposite="bpmnCollaborations")
UML.Package.bpmnCollaborations = association("bpmnCollaborations", BPMNCollaboration,
                                           composite=True, opposite="folder")
UML.NamedElement.namespace.add(BPMNCollaboration.folder)
UML.Namespace.ownedMember.add(UML.Package.bpmnCollaborations)
# A diagram may be a sibling of the folder containing its collaboration.
BPMNDiagram.bpmnCollaboration = association("bpmnCollaboration", BPMNCollaboration, upper=1)
UML.Element.owner.add(BPMNElement.container)
UML.Element.ownedElement.add(BPMNElement.ownedElements)

MODEL_TYPES = (BPMNElement, BPMNCollaboration, BPMNProcess, BPMNParticipant,
               BPMNLane, BPMNFlowNode, BPMNTask, BPMNSubProcess, BPMNEvent,
               BPMNGateway, BPMNFlow, BPMNSequenceFlow, BPMNMessageFlow,
               BPMNAssociation, BPMNTextAnnotation, BPMNDiagram)


def ancestors(element):
    """Walk native ownership with cycle protection, including the element."""
    seen = set()
    while element is not None and element.id not in seen:
        seen.add(element.id)
        yield element
        element = getattr(element, "owner", None)


def collaboration(element):
    if isinstance(element, BPMNDiagram):
        return element.bpmnCollaboration or collaboration(element.element)
    return next((e for e in ancestors(element) if isinstance(e, BPMNCollaboration)), None)


def process(element):
    if isinstance(element, BPMNParticipant):
        return element.processRef
    return next((e for e in ancestors(element) if isinstance(e, BPMNProcess)), None)


def scope(element):
    """Return the scope containing an element, not a subprocess's inner scope."""
    if isinstance(element, BPMNProcess):
        return element
    if isinstance(element, BPMNParticipant):
        return element.processRef
    return next((e for e in ancestors(getattr(element, "container", None))
                 if isinstance(e, (BPMNProcess, BPMNSubProcess))), None)


def participant(element):
    if isinstance(element, BPMNParticipant):
        return element
    root, proc = collaboration(element), process(element)
    if root is None or proc is None:
        return None
    return next((e for e in root.ownedElements
                 if isinstance(e, BPMNParticipant) and e.processRef is proc), None)


def descendants(element):
    pending, seen = [element], set()
    while pending:
        current = pending.pop()
        if current.id in seen:
            continue
        seen.add(current.id)
        yield current
        pending.extend(getattr(current, "ownedElements", ()))


def ownership_subtree(element):
    """Native composition, including package folders and diagram presentations."""
    pending, seen = [element], set()
    while pending:
        current = pending.pop()
        if current.id in seen:
            continue
        seen.add(current.id)
        yield current
        pending.extend(getattr(current, "ownedElement", ()))
        pending.extend(getattr(current, "ownedPresentation", ()))


def deletion_dependencies(element):
    """References that prevent a native deletion of this composition subtree.

    Lane assignment is optional: Gaphor can clear it when a lane is deleted.
    A participant and its process are siblings, so their joint removal requires
    the explicit operation rather than deleting either member independently.
    """
    if element.model is None:
        return []
    subtree = set(ownership_subtree(element))
    dependencies = {}
    if isinstance(element, BPMNParticipant) and element.processRef is not None:
        dependencies[element.processRef.id] = element.processRef
    for flow in element.model.select(BPMNFlow):
        if flow not in subtree and (flow.sourceRef in subtree or flow.targetRef in subtree):
            dependencies[flow.id] = flow
    for pool in element.model.select(BPMNParticipant):
        if pool not in subtree and pool.processRef in subtree:
            dependencies[pool.id] = pool
    for diagram in element.model.select(BPMNDiagram):
        if diagram not in subtree and diagram.bpmnCollaboration in subtree:
            dependencies[diagram.id] = diagram
    return list(dependencies.values())


def flow_type(kind):
    if kind in (BPMNSequenceFlow, "sequence", "SequenceFlow"):
        return BPMNSequenceFlow
    if kind in (BPMNMessageFlow, "message", "MessageFlow"):
        return BPMNMessageFlow
    if kind in (BPMNAssociation, "association", "Association"):
        return BPMNAssociation
    return None


def event_configuration_supported(event):
    combination = (event.eventKind, event.eventDefinition, event.eventDirection)
    supported = {
        ("START", "NONE", "CATCH"), ("START", "MESSAGE", "CATCH"),
        ("START", "TIMER", "CATCH"), ("INTERMEDIATE", "NONE", "THROW"),
        ("INTERMEDIATE", "MESSAGE", "CATCH"), ("INTERMEDIATE", "MESSAGE", "THROW"),
        ("INTERMEDIATE", "TIMER", "CATCH"), ("END", "NONE", "THROW"),
        ("END", "MESSAGE", "THROW"),
    }
    return (combination in supported and not (event.eventKind == "START"
            and isinstance(scope(event), BPMNSubProcess) and event.eventDefinition != "NONE"))


def can_connect(kind, source, target):
    """Endpoint/scope compatibility; graph cardinalities belong to validation."""
    cls = flow_type(kind)
    if not isinstance(source, BPMNElement) or not isinstance(target, BPMNElement):
        return False
    if source.model is not target.model:
        return False
    root = collaboration(source)
    if root is None or root is not collaboration(target):
        return False
    if any(isinstance(e, BPMNEvent) and not event_configuration_supported(e) for e in (source, target)):
        return False
    if cls is BPMNSequenceFlow:
        if not isinstance(source, BPMNFlowNode) or not isinstance(target, BPMNFlowNode):
            return False
        if scope(source) is None or scope(source) is not scope(target):
            return False
        if isinstance(source, BPMNEvent) and source.eventKind == "END":
            return False
        if isinstance(target, BPMNEvent) and target.eventKind == "START":
            return False
        return True
    if cls is BPMNMessageFlow:
        if source is target or participant(source) is None or participant(source) is participant(target):
            return False
        if participant(target) is None:
            return False
        for endpoint, sending in ((source, True), (target, False)):
            if isinstance(endpoint, BPMNEvent):
                if endpoint.eventDefinition != "MESSAGE":
                    return False
                if endpoint.eventKind == "START" and sending:
                    return False
                if endpoint.eventKind == "END" and not sending:
                    return False
                if endpoint.eventKind == "INTERMEDIATE" and (endpoint.eventDirection == "THROW") != sending:
                    return False
            elif not isinstance(endpoint, (BPMNParticipant, BPMNTask, BPMNSubProcess)):
                return False
        return True
    if cls is BPMNAssociation:
        allowed = (BPMNTextAnnotation, BPMNFlowNode, BPMNParticipant, BPMNLane)
        return (source is not target and isinstance(source, allowed) and isinstance(target, allowed)
                and (isinstance(source, BPMNTextAnnotation) or isinstance(target, BPMNTextAnnotation)))
    return False
