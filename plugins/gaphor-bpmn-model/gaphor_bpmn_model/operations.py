"""Factories and atomic edits for the persistent manual BPMN subset."""

from gaphor import UML
from gaphor.core import Transaction

from .model import (BPMNElement, BPMNCollaboration, BPMNProcess, BPMNParticipant,
                    BPMNLane, BPMNFlowNode, BPMNTask, BPMNSubProcess, BPMNEvent,
                    BPMNGateway, BPMNFlow, BPMNSequenceFlow, BPMNMessageFlow,
                    BPMNAssociation, BPMNTextAnnotation, BPMNDiagram,
                    ancestors, can_connect, collaboration, descendants, flow_type, process, scope)
from .validation import ModelError, raise_for_errors


def editable_fields(element):
    fields = {"name", "documentation", "container"}
    for cls, names in (
        (BPMNParticipant, ("processRef", "isClosed")),
        (BPMNFlowNode, ("lane",)),
        (BPMNEvent, ("eventKind", "eventDefinition", "eventDirection")),
        (BPMNGateway, ("gatewayKind",)),
        (BPMNFlow, ("sourceRef", "targetRef")),
        (BPMNSequenceFlow, ("flowKind", "conditionExpression")),
        (BPMNTextAnnotation, ("text",)),
    ):
        if isinstance(element, cls):
            fields.update(names)
    return fields


REFERENCE_FIELDS = {"container", "processRef", "lane", "sourceRef", "targetRef"}


def snapshot(element):
    """Editable camelCase fields; references are IDs, absent references are ''."""
    data = {"id": element.id}
    for name in sorted(editable_fields(element)):
        value = getattr(element, name)
        data[name] = (value.id if value else "") if name in REFERENCE_FIELDS else ("" if value is None else value)
    return data


def _resolve(element, changes):
    result = {}
    for name, value in changes.items():
        if name == "id":
            if value != element.id:
                raise ModelError("El borrador pertenece a otro elemento.")
            continue
        if name not in editable_fields(element):
            raise ModelError(f"Propiedad no editable: {name}.")
        if name in REFERENCE_FIELDS:
            if isinstance(value, str):
                ref = element.model.lookup(value) if value else None
                if value and ref is None:
                    raise ModelError("Una referencia ya no existe en este proyecto.")
                value = ref
            if value is not None and (not isinstance(value, BPMNElement) or value.model is not element.model):
                raise ModelError("La referencia debe pertenecer al mismo proyecto.")
            expected_type = {"container": BPMNElement, "processRef": BPMNProcess,
                             "lane": BPMNLane, "sourceRef": BPMNElement, "targetRef": BPMNElement}[name]
            if value is not None and not isinstance(value, expected_type):
                raise ModelError("El tipo de la referencia es incompatible con la propiedad.")
            if name == "container" and value is not None and element in ancestors(value):
                raise ModelError("La pertenencia no puede formar un ciclo.")
        elif name == "isClosed":
            if not isinstance(value, bool):
                raise ModelError("El estado cerrado debe ser booleano.")
        elif not isinstance(value, str) or "\x00" in value:
            raise ModelError("La propiedad requiere texto sin caracteres nulos.")
        result[name] = value
    return result


def update_element(element, changes, events, expected=None):
    if not isinstance(element, BPMNElement) or element.model.lookup(element.id) is not element:
        raise ModelError("El elemento ya no existe.")
    if expected is not None and snapshot(element) != expected:
        raise ModelError("El elemento cambió mientras editabas. Cierra y vuelve a abrir el editor.")
    changes = _resolve(element, changes)
    old_root = collaboration(element)
    with Transaction(events):
        for name, value in changes.items():
            setattr(element, name, value)
        if isinstance(element, BPMNParticipant) and not element.isClosed and element.processRef is None:
            proc = element.model.create(BPMNProcess)
            proc.name, proc.container = element.name, element.container
            element.processRef = proc
        root = collaboration(element)
        if root is None:
            raise ModelError("El elemento debe pertenecer a una colaboración BPMN.")
        raise_for_errors(root)
        if old_root is not None and old_root is not root:
            raise_for_errors(old_root)
    return element


def unique_name(base, elements):
    names = {e.name for e in elements}
    result, number = base, 2
    while result in names:
        result = f"{base}_{number}"
        number += 1
    return result


def create_collaboration(factory, events, name="Colaboración", *, folder=None, diagram_owner=None):
    """Create a collaboration with optional UML organization and diagram owner.

    The default retains the original ownership: the collaboration owns its
    diagram. An explicit diagram reference also identifies it when the diagram
    is organized as a sibling of the collaboration's UML folder.
    """
    for package in (folder, diagram_owner):
        if package is not None and (not isinstance(package, UML.Package)
                                    or package.model is not factory
                                    or factory.lookup(package.id) is not package):
            raise ModelError("La carpeta y el propietario del diagrama deben ser paquetes UML del mismo proyecto.")
    with Transaction(events):
        root = factory.create(BPMNCollaboration)
        root.name = unique_name(name, (e for e in factory.select(BPMNCollaboration) if e is not root))
        if folder is not None:
            root.folder = folder
        diagram = factory.create(BPMNDiagram)
        diagram.name, diagram.element = root.name, diagram_owner or root
        diagram.bpmnCollaboration = root
    return root, diagram


def create_participant(root, events, name="Participante", is_closed=False):
    if not isinstance(root, BPMNCollaboration):
        raise ModelError("El participante requiere una colaboración.")
    with Transaction(events):
        value = root.model.create(BPMNParticipant)
        value.name, value.container, value.isClosed = unique_name(name, root.ownedElements), root, is_closed
        if not is_closed:
            proc = root.model.create(BPMNProcess)
            proc.name, proc.container = value.name, root
            value.processRef = proc
        raise_for_errors(root)
    return value


def create_lane(proc, events, name="Carril"):
    if not isinstance(proc, BPMNProcess):
        raise ModelError("El carril requiere un proceso.")
    with Transaction(events):
        lane = proc.model.create(BPMNLane)
        lane.name, lane.container = unique_name(name, proc.ownedElements), proc
        raise_for_errors(collaboration(proc))
    return lane


def create_node(cls, container, events, name="", lane=None, **attributes):
    if cls not in (BPMNTask, BPMNSubProcess, BPMNEvent, BPMNGateway, BPMNTextAnnotation):
        raise ModelError("El tipo de nodo no está soportado.")
    allowed = (BPMNProcess, BPMNSubProcess)
    if cls is BPMNTextAnnotation:
        allowed += (BPMNCollaboration,)
    if not isinstance(container, allowed):
        raise ModelError("Selecciona un proceso o subproceso para el nodo.")
    with Transaction(events):
        node = container.model.create(cls)
        node.container, node.name = container, name
        if isinstance(node, BPMNFlowNode):
            node.lane = lane
        changes = _resolve(node, attributes)
        for key, value in changes.items():
            setattr(node, key, value)
        raise_for_errors(collaboration(node))
    return node


def create_flow(cls, source, target, events, **attributes):
    cls = flow_type(cls)
    if cls is None or not can_connect(cls, source, target):
        raise ModelError("Los extremos o ámbitos del flujo son incompatibles.")
    with Transaction(events):
        flow = source.model.create(cls)
        flow.sourceRef, flow.targetRef = source, target
        flow.container = scope(source) if cls is BPMNSequenceFlow else collaboration(source)
        for key, value in _resolve(flow, attributes).items():
            setattr(flow, key, value)
        raise_for_errors(collaboration(source))
    return flow


def delete_participant(value, events):
    """Delete a pool, its exclusive process and incident flows in one transaction.

    Raw ``unlink`` remains Gaphor's low-level primitive. Native UI deletion is
    protected by the BPMN ``deletable`` adapter; this explicit operation handles
    the aggregate that cannot be expressed through composite ownership alone.
    """
    if not isinstance(value, BPMNParticipant) or value.model.lookup(value.id) is not value:
        raise ModelError("El participante ya no existe.")
    model, root, proc = value.model, collaboration(value), value.processRef
    if root is None:
        raise ModelError("El participante debe pertenecer a una colaboración BPMN.")
    if proc is not None:
        if proc.model is not model or proc.container is not root:
            raise ModelError("El proceso del participante pertenece a una colaboración incompatible.")
        if any(pool is not value and pool.processRef is proc for pool in model.select(BPMNParticipant)):
            raise ModelError("El proceso está compartido por varios participantes. Resuelve sus referencias antes de eliminarlo.")
    subtree = set(descendants(value))
    if proc is not None:
        subtree.update(descendants(proc))
    incident = [flow for flow in model.select(BPMNFlow)
                if flow not in subtree and (flow.sourceRef in subtree or flow.targetRef in subtree)]
    with Transaction(events):
        for flow in incident:
            if model.lookup(flow.id) is flow:
                flow.unlink()
        if model.lookup(value.id) is value:
            value.unlink()
        if proc is not None and model.lookup(proc.id) is proc:
            proc.unlink()
