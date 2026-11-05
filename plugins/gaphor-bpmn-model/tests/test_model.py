import io
import unittest

from gi.repository import Gtk
from gaphor import UML
from gaphor.core import Transaction
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import ElementFactory
from gaphor.core.modeling.elementdispatcher import ElementDispatcher
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.services.undomanager import UndoManager
from gaphor.storage.load import load
from gaphor.storage.save import save
from gaphor.diagram.deletable import deletable

from gaphor_bpmn_model.model import *
from gaphor_bpmn_model.operations import *
from gaphor_bpmn_model.validation import ModelError, validate
from gaphor_bpmn_model.language import BPMNLanguage


class Fixture(unittest.TestCase):
    def setUp(self):
        Gtk.init()
        self.events = EventManager()
        self.language = ModelingLanguageService(self.events)
        self.language._modeling_languages["BPMN"] = BPMNLanguage()
        self.dispatcher = ElementDispatcher(self.events, self.language)
        self.model = ElementFactory(self.events, self.dispatcher)
        self.undo = UndoManager(self.events, self.model)
        self.root, self.diagram = create_collaboration(self.model, self.events)
        self.pool = self.participant("Empresa")
        self.proc = self.pool.processRef

    def tearDown(self):
        self.undo.shutdown()
        self.model.shutdown()
        self.dispatcher.shutdown()
        self.language.shutdown()

    def participant(self, name="Participante", is_closed=False):
        return create_participant(self.root, self.events, name, is_closed)

    def node(self, cls=BPMNTask, container=None, name="Tarea", lane=None, **attrs):
        return create_node(cls, container or self.proc, self.events, name, lane, **attrs)

    def flow(self, source, target, cls=BPMNSequenceFlow, **attrs):
        return create_flow(cls, source, target, self.events, **attrs)

    def errors(self):
        return [d for d in validate(self.root) if d.severity == "error"]


class ModelTests(Fixture):
    def test_native_ownership_separates_process_pool_and_lane(self):
        lane = create_lane(self.proc, self.events, "Operación")
        node = self.node(lane=lane)
        self.assertIs(self.pool.owner, self.root)
        self.assertIs(self.proc.owner, self.root)
        self.assertIs(node.owner, self.proc)
        self.assertIs(node.lane, lane)
        self.assertIn(node, self.proc.ownedElement)
        self.assertNotIn(node, lane.ownedElement)
        self.assertIs(participant(node), self.pool)
        self.assertIs(process(node), self.proc)
        self.assertEqual(self.errors(), [])

    def test_sequence_can_cross_lanes_in_one_process(self):
        a = self.node(lane=create_lane(self.proc, self.events, "A"))
        b = self.node(lane=create_lane(self.proc, self.events, "B"))
        flow = self.flow(a, b)
        self.assertIs(flow.container, self.proc)
        self.assertTrue(can_connect("sequence", a, b))

    def test_sequence_cannot_cross_processes(self):
        a = self.node()
        b = self.node(container=self.participant("Externo").processRef)
        before = self.model.size()
        self.assertFalse(can_connect("sequence", a, b))
        with self.assertRaises(ModelError):
            self.flow(a, b)
        self.assertEqual(self.model.size(), before)

    def test_sequence_cannot_cross_subprocess_boundary(self):
        sub = self.node(BPMNSubProcess)
        inner = self.node(container=sub)
        outer = self.node()
        self.assertIs(scope(sub), self.proc)
        self.assertIs(scope(inner), sub)
        self.assertFalse(can_connect("sequence", inner, outer))
        self.assertTrue(can_connect("sequence", sub, outer))

    def test_sequence_cannot_cross_sibling_subprocesses(self):
        left, right = self.node(BPMNSubProcess), self.node(BPMNSubProcess)
        a, b = self.node(container=left), self.node(container=right)
        self.assertFalse(can_connect("sequence", a, b))
        with self.assertRaises(ModelError):
            self.flow(a, b)

    def test_message_from_subprocess_child_to_external_pool_is_supported(self):
        sub = self.node(BPMNSubProcess)
        task = self.node(container=sub)
        external = self.participant("Externo", True)
        message = self.flow(task, external, BPMNMessageFlow)
        self.assertIs(message.container, self.root)
        self.assertIs(participant(task), self.pool)
        self.assertEqual(self.errors(), [])

    def test_start_and_end_sequence_directions(self):
        start = self.node(BPMNEvent, eventKind="START")
        end = self.node(BPMNEvent, eventKind="END", eventDirection="THROW")
        task = self.node()
        self.flow(start, task)
        self.flow(task, end)
        self.assertFalse(can_connect("sequence", task, start))
        self.assertFalse(can_connect("sequence", end, task))

    def test_event_combinations_rejected_atomically(self):
        start = self.node(BPMNEvent)
        before = snapshot(start)
        with self.assertRaises(ModelError):
            update_element(start, {"eventDirection": "THROW"}, self.events)
        self.assertEqual(snapshot(start), before)
        for attrs in (dict(eventKind="END", eventDefinition="TIMER", eventDirection="THROW"),
                      dict(eventKind="INTERMEDIATE", eventDefinition="NONE", eventDirection="CATCH")):
            count = self.model.size()
            with self.assertRaises(ModelError):
                self.node(BPMNEvent, **attrs)
            self.assertEqual(self.model.size(), count)

    def test_invalid_native_event_configuration_is_diagnosed(self):
        event = self.node(BPMNEvent, eventDefinition="MESSAGE")
        external = self.participant("Externo", True)
        with Transaction(self.events):
            event.eventDirection = "THROW"
        self.assertTrue(any(d.code == "event-configuration" and d.element_id == event.id for d in validate(self.root)))
        self.assertFalse(can_connect("message", external, event))

    def test_embedded_subprocess_start_supports_none_only(self):
        sub = self.node(BPMNSubProcess)
        self.node(BPMNEvent, container=sub)
        for definition in ("MESSAGE", "TIMER"):
            with self.assertRaises(ModelError):
                self.node(BPMNEvent, container=sub, eventDefinition=definition)

    def test_message_flows_require_different_participants(self):
        other = self.participant("Proveedor")
        a, b = self.node(), self.node(container=other.processRef)
        self.assertTrue(can_connect("message", a, b))
        flow = self.flow(a, b, BPMNMessageFlow)
        self.assertIs(flow.container, self.root)
        self.assertFalse(can_connect("message", a, self.node()))
        self.assertFalse(can_connect("message", self.pool, a))

    def test_message_directions_for_all_event_positions(self):
        other = self.participant("Externo", True)
        start = self.node(BPMNEvent, eventDefinition="MESSAGE")
        end = self.node(BPMNEvent, eventKind="END", eventDefinition="MESSAGE", eventDirection="THROW")
        catch = self.node(BPMNEvent, eventKind="INTERMEDIATE", eventDefinition="MESSAGE")
        throw = self.node(BPMNEvent, eventKind="INTERMEDIATE", eventDefinition="MESSAGE", eventDirection="THROW")
        for receiver in (start, catch):
            self.assertTrue(can_connect("message", other, receiver))
            self.assertFalse(can_connect("message", receiver, other))
        for sender in (end, throw):
            self.assertTrue(can_connect("message", sender, other))
            self.assertFalse(can_connect("message", other, sender))

    def test_timer_gateway_lane_annotation_reject_messages(self):
        other = self.participant("Externo", True)
        timer = self.node(BPMNEvent, eventDefinition="TIMER")
        gateway = self.node(BPMNGateway)
        lane = create_lane(self.proc, self.events)
        annotation = self.node(BPMNTextAnnotation, text="Nota")
        for target in (timer, gateway, lane, annotation):
            self.assertFalse(can_connect("message", other, target))
            self.assertFalse(can_connect("message", target, other))

    def test_intermediate_message_has_at_most_one_message_flow(self):
        other = self.participant("Externo", True)
        event = self.node(BPMNEvent, eventKind="INTERMEDIATE", eventDefinition="MESSAGE")
        self.flow(other, event, BPMNMessageFlow)
        before = self.model.size()
        with self.assertRaises(ModelError):
            self.flow(other, event, BPMNMessageFlow)
        self.assertEqual(self.model.size(), before)

    def test_message_start_accepts_multiple_incoming_message_flows(self):
        event = self.node(BPMNEvent, eventDefinition="MESSAGE")
        for name in ("A", "B"):
            self.flow(self.participant(name, True), event, BPMNMessageFlow)
        self.assertEqual(self.errors(), [])

    def test_association_can_explain_node_in_another_participant(self):
        note = create_node(BPMNTextAnnotation, self.root, self.events, text="Explicación")
        task = self.node(container=self.participant("Externo").processRef)
        association = self.flow(note, task, BPMNAssociation)
        self.assertIs(association.container, self.root)
        self.assertFalse(can_connect("association", self.node(), task))

    def test_default_sequence_is_unique_per_source(self):
        gateway = self.node(BPMNGateway)
        first = self.flow(gateway, self.node(), flowKind="DEFAULT")
        before = self.model.size()
        with self.assertRaises(ModelError):
            self.flow(gateway, self.node(), flowKind="DEFAULT")
        # The target node is created before the rejected flow transaction.
        self.assertEqual(self.model.size(), before + 1)
        self.assertEqual(first.flowKind, "DEFAULT")

    def test_parallel_gateway_rejects_conditional_and_default(self):
        gateway = self.node(BPMNGateway, gatewayKind="PARALLEL")
        task = self.node()
        for kind in ("CONDITIONAL", "DEFAULT"):
            with self.assertRaises(ModelError):
                self.flow(gateway, task, flowKind=kind)

    def test_incomplete_drawing_can_be_edited(self):
        gateway = self.node(BPMNGateway)
        self.assertTrue(any(d.code == "gateway-branches" for d in validate(self.root)))
        update_element(gateway, {"name": "Decidir", "gatewayKind": "PARALLEL"}, self.events)
        self.assertEqual(gateway.name, "Decidir")
        self.assertEqual(self.errors(), [])

    def test_change_event_configuration_preserves_existing_flow_on_error(self):
        task, target = self.node(), self.node(BPMNEvent, eventKind="END", eventDirection="THROW")
        flow = self.flow(task, target)
        before = snapshot(target)
        with self.assertRaises(ModelError):
            update_element(target, {"eventKind": "START", "eventDirection": "CATCH"}, self.events)
        self.assertEqual(snapshot(target), before)
        self.assertIs(flow.targetRef, target)

    def test_lane_assignment_from_other_process_is_rejected(self):
        node = self.node()
        lane = create_lane(self.participant("Otro").processRef, self.events)
        with self.assertRaises(ModelError):
            update_element(node, {"lane": lane.id}, self.events)
        self.assertIsNone(node.lane)

    def test_closed_participant_can_be_opened_and_empty_process_reused(self):
        pool = self.participant("Caja negra", True)
        self.assertIsNone(pool.processRef)
        update_element(pool, {"isClosed": False}, self.events)
        proc = pool.processRef
        self.assertIsInstance(proc, BPMNProcess)
        update_element(pool, {"isClosed": True}, self.events)
        update_element(pool, {"isClosed": False}, self.events)
        self.assertIs(pool.processRef, proc)

    def test_nonempty_participant_cannot_be_closed(self):
        self.node()
        with self.assertRaises(ModelError):
            update_element(self.pool, {"isClosed": True}, self.events)
        self.assertFalse(self.pool.isClosed)

    def test_optimistic_concurrency_and_missing_refs(self):
        task = self.node()
        old = snapshot(task)
        update_element(task, {"name": "Renombrada"}, self.events)
        with self.assertRaises(ModelError):
            update_element(task, {"name": "Obsoleta"}, self.events, old)
        with self.assertRaises(ModelError):
            update_element(task, {"lane": "missing-id"}, self.events)
        self.assertEqual(task.name, "Renombrada")

    def test_ownership_cycles_rejected_before_assignment(self):
        sub = self.node(BPMNSubProcess)
        child = self.node(BPMNSubProcess, container=sub)
        with self.assertRaises(ModelError):
            update_element(sub, {"container": child.id}, self.events)
        self.assertIs(sub.container, self.proc)

    def test_undo_redo_updates_one_transaction(self):
        task = self.node()
        before = snapshot(task)
        self.undo.clear_undo_stack()
        update_element(task, {"name": "Preparar", "documentation": "Instrucción"}, self.events)
        after = snapshot(task)
        self.undo.undo_transaction()
        self.assertEqual(snapshot(task), before)
        self.undo.redo_transaction()
        self.assertEqual(snapshot(task), after)

    def test_roundtrip_references_ownership_boolean_and_unicode(self):
        lane = create_lane(self.proc, self.events, "Operación")
        task = self.node(name="Inspección", lane=lane)
        note = self.node(BPMNTextAnnotation, text="Comprobar categoría áéíóú")
        self.flow(note, task, BPMNAssociation)
        self.participant("Externo", True)
        update_element(task, {"documentation": "Descripción multilínea\nSegunda línea"}, self.events)
        stream = io.StringIO()
        save(stream, self.model)
        self.assertIn("modelinglanguage/BPMN", stream.getvalue())
        other = ElementFactory()
        try:
            load(io.StringIO(stream.getvalue()), other, self.language)
            restored = other.lookup(task.id)
            self.assertEqual(snapshot(restored), snapshot(task))
            self.assertIs(restored.owner, other.lookup(self.proc.id))
            self.assertIs(restored.lane, other.lookup(lane.id))
            self.assertIs(other.lookup(self.pool.id).isClosed, False)
            self.assertIs(next(p for p in other.select(BPMNParticipant) if p.name == "Externo").isClosed, True)
            self.assertEqual([d for d in validate(other.lookup(self.root.id)) if d.severity == "error"], [])
        finally:
            other.shutdown()

    def test_without_language_fails_to_load_explicitly(self):
        stream = io.StringIO()
        save(stream, self.model)
        language = ModelingLanguageService(self.events)
        language._modeling_languages.pop("BPMN", None)
        other = ElementFactory()
        try:
            with self.assertRaises(ValueError):
                load(io.StringIO(stream.getvalue()), other, language)
        finally:
            other.shutdown()
            language.shutdown()

    def test_final_validation_promotes_gateway_and_intermediate_completeness(self):
        self.node(BPMNGateway)
        self.node(BPMNEvent, eventKind="INTERMEDIATE", eventDirection="THROW")
        draft = validate(self.root)
        final = validate(self.root, final=True)
        self.assertFalse(any(d.severity == "error" for d in draft))
        for code in ("gateway-branches", "no-incoming-sequence", "no-outgoing-sequence"):
            self.assertTrue(any(d.code == code and d.severity == "error" for d in final))

    def test_final_validation_requires_start_exit_and_end_entry(self):
        start = self.node(BPMNEvent)
        end = self.node(BPMNEvent, eventKind="END", eventDirection="THROW")
        final_errors = [d for d in validate(self.root, final=True) if d.severity == "error"]
        self.assertTrue(any(d.code == "no-outgoing-sequence" and d.element_id == start.id for d in final_errors))
        self.assertTrue(any(d.code == "no-incoming-sequence" and d.element_id == end.id for d in final_errors))

    def test_gateway_may_start_with_no_incoming_sequence(self):
        gateway = self.node(BPMNGateway, gatewayKind="PARALLEL")
        self.flow(gateway, self.node())
        self.flow(gateway, self.node())
        self.assertFalse(any(d.severity == "error" for d in validate(self.root, final=True)))

    def test_start_end_pair_is_scoped_and_both_optional(self):
        self.assertFalse(any(d.code == "start-end-pair" for d in validate(self.root, final=True)))
        self.node(BPMNEvent)
        self.assertTrue(any(d.code == "start-end-pair" and d.severity == "warning" for d in validate(self.root)))
        self.assertTrue(any(d.code == "start-end-pair" and d.severity == "error" for d in validate(self.root, final=True)))
        self.node(BPMNEvent, eventKind="END", eventDirection="THROW")
        sub = self.node(BPMNSubProcess)
        self.node(BPMNEvent, container=sub)
        pair_errors = [d for d in validate(self.root, final=True) if d.code == "start-end-pair"]
        self.assertEqual([d.element_id for d in pair_errors], [sub.id])

    def test_conditional_activity_requires_an_alternative_on_final_validation(self):
        source, target = self.node(), self.node()
        self.flow(source, target, flowKind="CONDITIONAL", conditionExpression="importe > 0")
        self.assertTrue(any(d.code == "conditional-needs-alternative" and d.severity == "warning" for d in validate(self.root)))
        self.assertTrue(any(d.code == "conditional-needs-alternative" and d.severity == "error" for d in validate(self.root, final=True)))
        self.flow(source, self.node())
        self.assertFalse(any(d.code == "conditional-needs-alternative" for d in validate(self.root, final=True)))

    def test_ignored_condition_is_reported_without_blocking_edit(self):
        source, target = self.node(), self.node()
        flow = self.flow(source, target, conditionExpression="literal")
        self.assertEqual(flow.flowKind, "NORMAL")
        self.assertTrue(any(d.code == "ignored-condition" for d in validate(self.root)))

    def test_deletion_dependencies_include_pool_process_and_external_flows(self):
        task, target = self.node(), self.node()
        flow = self.flow(task, target)
        self.assertIn(self.proc, deletion_dependencies(self.pool))
        self.assertIn(self.pool, deletion_dependencies(self.proc))
        self.assertIn(flow, deletion_dependencies(task))
        self.assertEqual(deletion_dependencies(self.root), [])

    def test_lane_unlink_clears_only_assignment_and_undo_restores_it(self):
        lane = create_lane(self.proc, self.events, "Operación")
        task = self.node(lane=lane)
        before = snapshot(lane)
        self.assertEqual(deletion_dependencies(lane), [])
        self.undo.clear_undo_stack()
        with Transaction(self.events):
            lane.unlink()
        self.assertIsNone(task.lane)
        self.assertIs(task.container, self.proc)
        self.assertEqual(self.errors(), [])
        self.undo.undo_transaction()
        restored = self.model.lookup(lane.id)
        self.assertIsInstance(restored, BPMNLane)
        self.assertEqual(snapshot(restored), before)
        self.assertIs(task.lane, restored)
        self.assertIs(restored.container, self.proc)
        self.assertIs(task.container, self.proc)
        self.assertIn(restored, self.proc.ownedElements)
        self.assertEqual(self.errors(), [])

    def test_lane_with_annotation_association_has_deletion_dependency(self):
        lane = create_lane(self.proc, self.events, "Operación")
        note = self.node(BPMNTextAnnotation, text="Responsabilidad")
        association = self.flow(note, lane, BPMNAssociation)
        self.assertIn(association, deletion_dependencies(lane))

    def test_subprocess_external_message_protects_entire_subtree(self):
        sub = self.node(BPMNSubProcess)
        task = self.node(container=sub)
        external = self.participant("Externo", True)
        message = self.flow(task, external, BPMNMessageFlow)
        self.assertIn(message, deletion_dependencies(sub))

    def test_delete_participant_removes_aggregate_and_incident_flows_atomically(self):
        external = self.participant("Cliente")
        receiving = self.node(container=external.processRef)
        lane = create_lane(self.proc, self.events, "Operación")
        source, target = self.node(lane=lane), self.node()
        sequence = self.flow(source, target)
        message = self.flow(source, receiving, BPMNMessageFlow)
        note = create_node(BPMNTextAnnotation, self.root, self.events, text="Explicar pool")
        association = self.flow(note, self.pool, BPMNAssociation)
        removed = [self.pool, self.proc, lane, source, target, sequence, message, association]
        before = {e.id: snapshot(e) for e in removed}
        self.undo.clear_undo_stack()
        delete_participant(self.pool, self.events)
        self.assertTrue(all(self.model.lookup(e.id) is None for e in removed))
        self.assertIs(self.model.lookup(external.id), external)
        self.assertIs(self.model.lookup(receiving.id), receiving)
        self.assertIs(receiving.container, external.processRef)
        self.assertIs(self.model.lookup(note.id), note)
        self.assertEqual(self.errors(), [])
        self.undo.undo_transaction()
        for element in removed:
            restored = self.model.lookup(element.id)
            self.assertIsInstance(restored, type(element))
            self.assertEqual(snapshot(restored), before[element.id])
        restored_pool, restored_process = self.model.lookup(self.pool.id), self.model.lookup(self.proc.id)
        restored_source, restored_target = self.model.lookup(source.id), self.model.lookup(target.id)
        restored_lane = self.model.lookup(lane.id)
        restored_sequence = self.model.lookup(sequence.id)
        restored_message = self.model.lookup(message.id)
        restored_association = self.model.lookup(association.id)
        self.assertIs(restored_pool.processRef, restored_process)
        self.assertIs(restored_pool.container, self.root)
        self.assertIs(restored_process.container, self.root)
        self.assertIs(restored_source.container, restored_process)
        self.assertIs(restored_target.container, restored_process)
        self.assertIs(restored_lane.container, restored_process)
        self.assertIs(restored_source.lane, restored_lane)
        self.assertIs(restored_sequence.sourceRef, restored_source)
        self.assertIs(restored_sequence.targetRef, restored_target)
        self.assertIs(restored_sequence.container, restored_process)
        self.assertIs(restored_message.sourceRef, restored_source)
        self.assertIs(restored_message.targetRef, receiving)
        self.assertIs(restored_message.container, self.root)
        self.assertIs(restored_association.sourceRef, note)
        self.assertIs(restored_association.targetRef, restored_pool)
        self.assertIs(restored_association.container, self.root)
        self.assertEqual(self.errors(), [])
        self.undo.redo_transaction()
        self.assertTrue(all(self.model.lookup(e.id) is None for e in removed))
        self.assertEqual(self.errors(), [])

    def test_delete_closed_participant_removes_messages_without_process(self):
        external = self.participant("Externo", True)
        message = self.flow(self.node(), external, BPMNMessageFlow)
        delete_participant(external, self.events)
        self.assertIsNone(self.model.lookup(external.id))
        self.assertIsNone(self.model.lookup(message.id))
        self.assertIs(self.model.lookup(self.proc.id), self.proc)
        self.assertEqual(self.errors(), [])

    def test_delete_participant_rejects_shared_process_without_partial_changes(self):
        extra = self.participant("Ambiguo", True)
        with Transaction(self.events):
            extra.processRef = self.proc
        before_ids = {e.id for e in self.model.select()}
        with self.assertRaises(ModelError):
            delete_participant(self.pool, self.events)
        self.assertEqual({e.id for e in self.model.select()}, before_ids)
        self.assertIs(extra.processRef, self.proc)
        self.assertIs(self.pool.processRef, self.proc)

    def organized_collaboration(self):
        with Transaction(self.events):
            parent = self.model.create(UML.Package)
            parent.name = "ingreso materiales"
            folder = self.model.create(UML.Package)
            folder.name, folder.nestingPackage = "childs", parent
        root, diagram = create_collaboration(self.model, self.events, "Ingreso PT",
                                             folder=folder, diagram_owner=parent)
        return parent, folder, root, diagram

    def test_organized_collaboration_has_one_semantic_owner_and_explicit_diagram_ref(self):
        parent, folder, root, diagram = self.organized_collaboration()
        self.assertIsNone(root.container)
        self.assertIs(root.folder, folder)
        self.assertIs(root.owner, folder)
        self.assertIs(root.namespace, folder)
        self.assertIn(root, folder.ownedElement)
        self.assertIn(root, folder.ownedMember)
        self.assertIs(diagram.element, parent)
        self.assertIs(diagram.bpmnCollaboration, root)
        self.assertIs(collaboration(diagram), root)
        self.assertIn(diagram, parent.ownedDiagram)
        self.assertNotIn(diagram, root.ownedDiagram)
        self.assertEqual([d for d in validate(root) if d.severity == "error"], [])

    def test_organized_collaboration_roundtrip_preserves_folder_and_diagram_references(self):
        parent, folder, root, diagram = self.organized_collaboration()
        pool = create_participant(root, self.events, "Almacén")
        task = create_node(BPMNTask, pool.processRef, self.events, "Recibir PT")
        xml = io.StringIO()
        save(xml, self.model)
        other = ElementFactory()
        try:
            load(io.StringIO(xml.getvalue()), other, self.language)
            recovered = other.lookup(root.id)
            recovered_diagram = other.lookup(diagram.id)
            self.assertIs(recovered.folder, other.lookup(folder.id))
            self.assertIs(recovered.namespace, other.lookup(folder.id))
            self.assertIs(recovered_diagram.element, other.lookup(parent.id))
            self.assertIs(recovered_diagram.bpmnCollaboration, recovered)
            self.assertIs(collaboration(recovered_diagram), recovered)
            self.assertIs(other.lookup(task.id).container, other.lookup(pool.processRef.id))
            self.assertEqual([d for d in validate(recovered) if d.severity == "error"], [])
        finally:
            other.shutdown()

    def test_legacy_diagram_without_explicit_collaboration_still_resolves(self):
        with Transaction(self.events):
            self.diagram.bpmnCollaboration = None
        self.assertIs(collaboration(self.diagram), self.root)
        self.assertEqual(self.errors(), [])
        xml = io.StringIO()
        save(xml, self.model)
        other = ElementFactory()
        try:
            load(io.StringIO(xml.getvalue()), other, self.language)
            self.assertIsNone(other.lookup(self.diagram.id).bpmnCollaboration)
            self.assertIs(collaboration(other.lookup(self.diagram.id)), other.lookup(self.root.id))
        finally:
            other.shutdown()

    def test_collaboration_factory_rejects_external_folder_before_mutating(self):
        other = ElementFactory()
        try:
            folder = other.create(UML.Package)
            before = self.model.size()
            with self.assertRaises(ModelError):
                create_collaboration(self.model, self.events, folder=folder)
            with self.assertRaises(ModelError):
                create_collaboration(self.model, self.events, diagram_owner=folder)
            self.assertEqual(self.model.size(), before)
        finally:
            other.shutdown()

    def test_organization_guard_blocks_childs_with_external_sibling_diagram(self):
        parent, folder, root, diagram = self.organized_collaboration()
        self.assertIn(diagram, deletion_dependencies(root))
        self.assertIn(diagram, deletion_dependencies(folder))
        self.assertFalse(deletable(root))
        self.assertFalse(deletable(folder))
        self.assertEqual(deletion_dependencies(parent), [])
        self.assertTrue(deletable(parent))

    def test_diagram_reference_must_agree_with_semantic_owner(self):
        _, _, other_root, _ = self.organized_collaboration()
        with Transaction(self.events):
            self.diagram.bpmnCollaboration = other_root
        self.assertTrue(any(d.code == "diagram-collaboration" for d in validate(self.root)))

    def test_organized_creation_undo_redo_restores_all_reference_ids(self):
        with Transaction(self.events):
            parent, folder = self.model.create(UML.Package), self.model.create(UML.Package)
            folder.nestingPackage = parent
        self.undo.clear_undo_stack()
        root, diagram = create_collaboration(self.model, self.events, folder=folder, diagram_owner=parent)
        ids = root.id, diagram.id
        self.undo.undo_transaction()
        self.assertTrue(all(self.model.lookup(id_) is None for id_ in ids))
        self.undo.redo_transaction()
        restored_root, restored_diagram = (self.model.lookup(id_) for id_ in ids)
        self.assertIs(restored_root.folder, folder)
        self.assertIs(restored_diagram.element, parent)
        self.assertIs(restored_diagram.bpmnCollaboration, restored_root)
        self.assertEqual([d for d in validate(restored_root) if d.severity == "error"], [])
