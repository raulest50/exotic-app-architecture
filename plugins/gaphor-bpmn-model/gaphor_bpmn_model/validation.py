"""Structural validation of the supported manual BPMN subset.

Incomplete drawings produce warnings. Only errors block editing operations.
Validation does not execute a process or certify BPMN conformance.
"""

from dataclasses import dataclass
from gaphor import UML

from .model import (BPMNElement, BPMNCollaboration, BPMNProcess, BPMNParticipant,
                    BPMNLane, BPMNFlowNode, BPMNTask, BPMNSubProcess, BPMNEvent,
                    BPMNGateway, BPMNFlow, BPMNSequenceFlow, BPMNMessageFlow,
                    BPMNAssociation, BPMNTextAnnotation, BPMNDiagram, can_connect,
                    collaboration, descendants, event_configuration_supported,
                    participant, process, scope)

EVENT_KINDS = ("START", "INTERMEDIATE", "END")
EVENT_DEFINITIONS = ("NONE", "MESSAGE", "TIMER")
EVENT_DIRECTIONS = ("CATCH", "THROW")
GATEWAY_KINDS = ("EXCLUSIVE", "PARALLEL")
FLOW_KINDS = ("NORMAL", "CONDITIONAL", "DEFAULT")


class ModelError(ValueError):
    pass


@dataclass(frozen=True)
class Diagnostic:
    severity: str
    code: str
    message: str
    element_id: str


def validate(root, *, final=False):
    """Return errors plus completeness warnings, without changing the model."""
    issues = []
    incomplete_severity = "error" if final else "warning"

    def add(element, code, message, severity="error"):
        issues.append(Diagnostic(severity, code, message, element.id))

    if not isinstance(root, BPMNCollaboration):
        return [Diagnostic("error", "collaboration-required", "Selecciona una colaboración BPMN.", getattr(root, "id", ""))]
    if root.folder is not None and (not isinstance(root.folder, UML.Package)
                                    or root.folder.model is not root.model
                                    or root.model.lookup(root.folder.id) is not root.folder):
        add(root, "collaboration-folder", "La carpeta de la colaboración debe ser un paquete UML del mismo proyecto.")
    for diagram in root.model.select(BPMNDiagram):
        explicit = diagram.bpmnCollaboration
        owner_root = collaboration(diagram.element)
        if owner_root is root and explicit is not None and explicit is not root:
            add(diagram, "diagram-collaboration", "El propietario y la referencia explícita del diagrama indican colaboraciones distintas.")
        if explicit is root:
            owner = diagram.element
            if owner is None or (owner is not root and not isinstance(owner, UML.Package)):
                add(diagram, "diagram-owner", "El diagrama debe pertenecer a su colaboración o a un paquete UML.")
            elif owner.model is not root.model or root.model.lookup(owner.id) is not owner:
                add(diagram, "diagram-owner", "El propietario del diagrama debe pertenecer al mismo proyecto.")
    elements = list(descendants(root))
    flows = [e for e in elements if isinstance(e, BPMNFlow)]
    for element in elements:
        if "\x00" in (element.name or "") or "\x00" in (element.documentation or ""):
            add(element, "invalid-text", "El texto no puede contener caracteres nulos.")
        if collaboration(element) is not root:
            add(element, "ownership-cycle", "La pertenencia contiene un ciclo o una raíz incompatible.")
        if isinstance(element, BPMNCollaboration):
            if element is not root or element.container is not None:
                add(element, "nested-collaboration", "La colaboración debe ser raíz del modelo BPMN.")
        elif isinstance(element, (BPMNParticipant, BPMNProcess)):
            if element.container is not root:
                add(element, "collaboration-owner", "Los participantes y procesos pertenecen a la colaboración.")
        elif isinstance(element, BPMNLane):
            if not isinstance(element.container, BPMNProcess):
                add(element, "lane-owner", "Los carriles pertenecen directamente a un proceso.")
        elif isinstance(element, (BPMNFlowNode, BPMNTextAnnotation)):
            allowed = (BPMNProcess, BPMNSubProcess)
            if isinstance(element, BPMNTextAnnotation):
                allowed += (BPMNCollaboration,)
            if not isinstance(element.container, allowed):
                add(element, "node-owner", "El elemento necesita un proceso o subproceso compatible.")
        if element.ownedElements and not isinstance(element, (BPMNCollaboration, BPMNProcess, BPMNSubProcess)):
            add(element, "unsupported-owner", "Este tipo no puede contener elementos BPMN.")
        if isinstance(element, BPMNParticipant):
            proc = element.processRef
            if proc is not None and (proc.container is not root or proc.model is not element.model):
                add(element, "participant-process", "El proceso debe pertenecer a la misma colaboración.")
            if not element.isClosed and proc is None:
                add(element, "missing-process", "Un participante expandido requiere un proceso.")
            if element.isClosed and proc is not None and any(isinstance(e, (BPMNFlowNode, BPMNLane)) for e in proc.ownedElements):
                add(element, "closed-participant-content", "El participante con nodos o carriles no puede cerrarse.")
        if isinstance(element, BPMNProcess):
            pools = [e for e in elements if isinstance(e, BPMNParticipant) and e.processRef is element]
            if len(pools) != 1:
                add(element, "process-participant", "Cada proceso debe estar asociado a un único participante.")
        if isinstance(element, BPMNFlowNode):
            if element.lane is not None and (not isinstance(element.lane, BPMNLane) or process(element.lane) is not process(element)):
                add(element, "lane-process", "El carril debe pertenecer al mismo proceso del nodo.")
            pool = participant(element)
            if pool is not None and pool.isClosed:
                add(element, "closed-participant-node", "No se admiten nodos dentro de un participante cerrado.")
        if isinstance(element, BPMNLane):
            pool = participant(element)
            if pool is not None and pool.isClosed:
                add(element, "closed-participant-lane", "No se admiten carriles en un participante cerrado.")
        if isinstance(element, BPMNEvent):
            if not event_configuration_supported(element):
                add(element, "event-configuration", "La combinación de evento, definición y dirección no está soportada.")
        if isinstance(element, BPMNGateway) and element.gatewayKind not in GATEWAY_KINDS:
            add(element, "gateway-kind", "El tipo de compuerta no está soportado.")
        if isinstance(element, BPMNFlow):
            if not can_connect(type(element), element.sourceRef, element.targetRef):
                add(element, "flow-endpoints", "Los extremos o ámbitos del flujo son incompatibles.")
            expected = root if isinstance(element, (BPMNMessageFlow, BPMNAssociation)) else scope(element.sourceRef)
            if element.container is not expected:
                add(element, "flow-owner", "El flujo debe pertenecer al ámbito de sus extremos.")
        if isinstance(element, BPMNSequenceFlow):
            if element.flowKind not in FLOW_KINDS:
                add(element, "flow-kind", "El tipo de flujo de secuencia no está soportado.")
            if element.flowKind != "NORMAL":
                source = element.sourceRef
                if not isinstance(source, (BPMNTask, BPMNSubProcess)) and not (isinstance(source, BPMNGateway) and source.gatewayKind == "EXCLUSIVE"):
                    add(element, "flow-source-kind", "Un flujo condicional o predeterminado requiere una actividad o compuerta exclusiva.")
            if element.flowKind == "CONDITIONAL" and not element.conditionExpression.strip():
                add(element, "conditional-expression", "Falta la condición del flujo condicional.", incomplete_severity)
            if element.flowKind in ("NORMAL", "DEFAULT") and element.conditionExpression.strip():
                add(element, "ignored-condition", "La expresión se conserva como texto, pero sólo un flujo condicional la utiliza.", "warning")
    for element in elements:
        incoming = [f for f in flows if isinstance(f, BPMNSequenceFlow) and f.targetRef is element]
        outgoing = [f for f in flows if isinstance(f, BPMNSequenceFlow) and f.sourceRef is element]
        if isinstance(element, BPMNFlowNode):
            strict_node = isinstance(element, BPMNEvent)
            degree_severity = incomplete_severity if strict_node else "warning"
            defaults = [f for f in outgoing if f.flowKind == "DEFAULT"]
            if len(defaults) > 1:
                add(element, "multiple-default-flows", "Sólo puede existir un flujo predeterminado por nodo.")
            if not incoming and not (isinstance(element, BPMNEvent) and element.eventKind == "START"):
                add(element, "no-incoming-sequence", "El nodo no tiene flujo de secuencia entrante.", degree_severity)
            if not outgoing and not (isinstance(element, BPMNEvent) and element.eventKind == "END"):
                add(element, "no-outgoing-sequence", "El nodo no tiene flujo de secuencia saliente.", degree_severity)
            if isinstance(element, (BPMNTask, BPMNSubProcess)) and len(outgoing) == 1 and outgoing[0].flowKind == "CONDITIONAL":
                add(element, "conditional-needs-alternative", "La actividad con una salida condicional necesita otra salida.", incomplete_severity)
        if isinstance(element, BPMNEvent) and element.eventDefinition == "MESSAGE" and element.eventKind != "START":
            messages = [f for f in flows if isinstance(f, BPMNMessageFlow) and (f.sourceRef is element or f.targetRef is element)]
            if len(messages) > 1:
                add(element, "multiple-event-messages", "Un evento de mensaje admite como máximo un flujo de mensaje.")
        if isinstance(element, BPMNGateway) and len(incoming) < 2 and len(outgoing) < 2:
            add(element, "gateway-branches", "La compuerta debe reunir o dividir al menos dos secuencias.", incomplete_severity)
        if isinstance(element, (BPMNProcess, BPMNSubProcess)):
            starts = any(isinstance(e, BPMNEvent) and e.eventKind == "START" for e in element.ownedElements)
            ends = any(isinstance(e, BPMNEvent) and e.eventKind == "END" for e in element.ownedElements)
            if starts != ends:
                add(element, "start-end-pair", "El ámbito con un evento de inicio o fin requiere al menos uno de cada tipo.", incomplete_severity)
    return issues


def raise_for_errors(root):
    errors = [d for d in validate(root) if d.severity == "error"]
    if errors:
        raise ModelError("\n".join(dict.fromkeys(d.message for d in errors)))
    return validate(root)
