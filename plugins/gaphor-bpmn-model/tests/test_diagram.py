"""Native Gaphor presentation, connector, persistence and clipboard checks."""

import io
import os
from pathlib import Path
import unittest

from gi.repository import Gtk
from gaphas.connector import Connector as ConnectorAspect
from gaphor import UML
from gaphor.core import Transaction
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import ElementFactory, StyleSheet
from gaphor.core.modeling.elementdispatcher import ElementDispatcher
from gaphor.diagram.copypaste import copy_full, paste_full, paste_link
from gaphor.diagram.deletable import deletable
from gaphor.diagram.drop import drop
from gaphor.diagram.export import save_png, save_svg
from gaphor.diagram.group import change_owner, group, owner, owns, Root
from gaphor.diagram.presentation import connect
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.services.undomanager import UndoManager
from gaphor.storage.load import load
from gaphor.storage.save import save
from gaphor.UML.treemodel import TreeModel

from gaphor_bpmn_model import diagram as view
from gaphor_bpmn_model.language import BPMNLanguage, bpmn_tools, primary_process
from gaphor_bpmn_model.model import (
    BPMNCollaboration, BPMNProcess, BPMNParticipant, BPMNLane, BPMNTask,
    BPMNSubProcess, BPMNEvent, BPMNGateway, BPMNSequenceFlow, BPMNMessageFlow,
    BPMNAssociation, BPMNTextAnnotation, BPMNDiagram,
    collaboration,
)
from gaphor_bpmn_model.operations import create_collaboration, create_participant, create_lane, create_node, create_flow
from gaphor_bpmn_model.validation import validate


class DiagramTests(unittest.TestCase):
    def setUp(self):
        Gtk.init()
        self.events = EventManager()
        self.language = ModelingLanguageService(self.events)
        self.language._modeling_languages["BPMN"] = BPMNLanguage()
        self.dispatcher = ElementDispatcher(self.events, self.language)
        self.factory = ElementFactory(self.events, self.dispatcher)
        self.undo = UndoManager(self.events, self.factory)
        self.root, self.diagram = create_collaboration(self.factory, self.events)
        self.pool = create_participant(self.root, self.events, name="Exotic")
        self.proc = self.pool.processRef

    def tearDown(self):
        self.undo.shutdown()
        self.factory.shutdown()
        self.dispatcher.shutdown()
        self.language.shutdown()

    def node(self, cls=BPMNTask, name="Tarea", **attributes):
        return create_node(cls, self.proc, self.events, name=name, **attributes)

    def visual(self, subject, x=30, y=30):
        with Transaction(self.events):
            return drop(subject, self.diagram, x, y)

    def tool(self, tool_id, parent=None):
        tool = next(t for t in bpmn_tools.tools if t.id == tool_id)
        with Transaction(self.events):
            return tool.item_factory(self.diagram, parent)

    def line(self, source, target, cls=view.BPMNSequenceFlowItem):
        with Transaction(self.events):
            line = self.diagram.create(cls)
            line.head.pos = source.matrix_i2c.transform_point(source.width / 2, source.height / 2)
            line.tail.pos = target.matrix_i2c.transform_point(target.width / 2, target.height / 2)
            connect(line, line.head, target)
            connect(line, line.tail, source)
        return line

    def test_native_language_and_new_diagram_initial_pool(self):
        language = BPMNLanguage()
        self.assertIs(language.lookup_element("BPMNTask"), BPMNTask)
        self.assertIs(language.lookup_element("BPMNTaskItem"), view.BPMNTaskItem)
        with Transaction(self.events):
            native = language.diagram_types[0].create(self.factory, None)
        self.assertIsInstance(native.element, BPMNCollaboration)
        self.assertIsNotNone(primary_process(native))
        self.assertTrue(any(isinstance(i, view.BPMNParticipantItem) for i in native.get_all_items()))

    def packaged_layout(self):
        with Transaction(self.events):
            host = self.factory.create(UML.Package)
            host.name = "ingreso materiales"
            children = self.factory.create(UML.Package)
            children.name, children.nestingPackage = "childs", host
            self.root.folder = children
            self.diagram.element = host
            self.diagram.bpmnCollaboration = self.root
        return host, children

    def test_folder_integrates_namespace_and_native_ownership(self):
        host, children = self.packaged_layout()
        self.assertIsNone(self.root.container)
        self.assertIs(self.root.folder, children)
        self.assertIs(self.root.namespace, children)
        self.assertIs(self.root.owner, children)
        self.assertIs(owner(self.root), children)
        self.assertIn(self.root, children.ownedMember)
        self.assertIn(self.root, children.ownedElement)
        self.assertIn(self.root, owns(children))
        self.assertIs(self.diagram.element, host)
        self.assertIs(collaboration(self.diagram), self.root)

    def test_native_package_diagram_keeps_owner_and_one_collaboration(self):
        with Transaction(self.events):
            host = self.factory.create(UML.Package)
            host.name = "Proceso nuevo"
            native = BPMNLanguage().diagram_types[0].create(self.factory, host)
        root = native.bpmnCollaboration
        self.assertIs(native.element, host)
        self.assertIs(root.folder, host)
        self.assertIsNone(root.container)
        roots_before = len(list(self.factory.select(BPMNCollaboration)))
        pool_tool = next(t for t in bpmn_tools.tools if t.id == "bpmn-pool-closed")
        annotation_tool = next(t for t in bpmn_tools.tools if t.id == "bpmn-annotation")
        with Transaction(self.events):
            pool = pool_tool.item_factory(native)
            annotation = annotation_tool.item_factory(native)
        self.assertIs(pool.subject.container, root)
        self.assertIs(annotation.subject.container, root)
        self.assertIs(native.element, host)
        self.assertEqual(len(list(self.factory.select(BPMNCollaboration))), roots_before)

    def test_packaged_diagram_toolbox_resolves_explicit_collaboration(self):
        host, children = self.packaged_layout()
        roots_before = len(list(self.factory.select(BPMNCollaboration)))
        pool = self.visual(self.pool)
        lane = self.tool("bpmn-lane", pool)
        task = self.tool("bpmn-task", lane)
        annotation = self.tool("bpmn-annotation")
        self.assertIs(primary_process(self.diagram), self.proc)
        self.assertIs(task.subject.container, self.proc)
        self.assertIs(annotation.subject.container, self.root)
        self.assertIs(self.root.folder, children)
        self.assertIs(self.diagram.element, host)
        self.assertEqual(len(list(self.factory.select(BPMNCollaboration))), roots_before)

    def test_tree_model_tracks_folder_grouping_and_undo(self):
        host, children = self.packaged_layout()
        tree = TreeModel(self.events, self.factory)
        try:
            tree.child_model(tree.tree_item_for_element(host))
            child_branch = tree.child_model(tree.tree_item_for_element(children))
            self.assertIn(self.root, [item.element for item in child_branch])
            self.assertNotIn(self.root, [item.element for item in tree.root])
            with Transaction(self.events):
                destination = self.factory.create(UML.Package)
                destination.name, destination.nestingPackage = "Otro grupo", host
            self.undo.clear_undo_stack()
            with Transaction(self.events):
                self.assertTrue(change_owner(destination, self.root))
            destination_branch = tree.child_model(tree.tree_item_for_element(destination))
            self.assertIs(self.root.folder, destination)
            self.assertIn(self.root, [item.element for item in destination_branch])
            self.assertNotIn(self.root, [item.element for item in child_branch])
            self.undo.undo_transaction()
            restored_branch = tree.child_model(tree.tree_item_for_element(children))
            self.assertIs(self.root.folder, children)
            self.assertIn(self.root, [item.element for item in restored_branch])
        finally:
            tree.shutdown()

    def test_packaged_roundtrip_preserves_folder_and_diagram_reference(self):
        host, children = self.packaged_layout()
        stream = io.StringIO(); save(stream, self.factory)
        self.assertIn("<bpmnCollaborations>", stream.getvalue())
        self.assertIn("<bpmnCollaboration>", stream.getvalue())
        other = ElementFactory()
        try:
            load(io.StringIO(stream.getvalue()), other, self.language)
            restored = other.lookup(self.root.id)
            diagram = other.lookup(self.diagram.id)
            self.assertIs(restored.folder, other.lookup(children.id))
            self.assertIs(restored.namespace, other.lookup(children.id))
            self.assertIsNone(restored.container)
            self.assertIs(diagram.element, other.lookup(host.id))
            self.assertIs(diagram.bpmnCollaboration, restored)
            self.assertIs(collaboration(diagram), restored)
        finally:
            other.shutdown()

    def test_legacy_diagram_without_explicit_reference_stays_compatible(self):
        with Transaction(self.events):
            self.diagram.bpmnCollaboration = None
        self.assertIs(self.diagram.element, self.root)
        self.assertIsNone(self.root.folder)
        self.assertIs(owner(self.root), Root)
        self.assertIs(collaboration(self.diagram), self.root)
        self.assertIs(primary_process(self.diagram), self.proc)
        stream = io.StringIO(); save(stream, self.factory)
        self.assertNotIn("<folder>", stream.getvalue())
        self.assertNotIn("<bpmnCollaboration>", stream.getvalue())
        other = ElementFactory()
        try:
            load(io.StringIO(stream.getvalue()), other, self.language)
            diagram = other.lookup(self.diagram.id)
            self.assertIsNone(diagram.bpmnCollaboration)
            self.assertIs(collaboration(diagram), other.lookup(self.root.id))
        finally:
            other.shutdown()

    def test_folder_delete_is_blocked_until_external_diagram_removed(self):
        host, children = self.packaged_layout()
        self.assertFalse(deletable(self.root))
        self.assertFalse(deletable(children))
        self.assertTrue(deletable(host))
        with Transaction(self.events):
            unrelated = self.factory.create(UML.Package)
        self.assertTrue(deletable(unrelated))
        with Transaction(self.events):
            self.diagram.unlink()
        self.assertTrue(deletable(self.root))
        self.assertTrue(deletable(children))

    def test_complete_package_delete_and_undo_restore_reference(self):
        host, children = self.packaged_layout()
        ids = (host.id, children.id, self.root.id, self.diagram.id, self.pool.id, self.proc.id)
        self.undo.clear_undo_stack()
        with Transaction(self.events):
            host.unlink()
        self.assertTrue(all(self.factory.lookup(identifier) is None for identifier in ids))
        self.undo.undo_transaction()
        restored = self.factory.lookup(self.root.id)
        self.assertIs(restored.folder, self.factory.lookup(children.id))
        self.assertIs(self.factory.lookup(self.diagram.id).bpmnCollaboration, restored)
        self.assertIs(self.factory.lookup(self.diagram.id).element, self.factory.lookup(host.id))

    def test_native_deletion_protects_empty_pool_and_referenced_process(self):
        self.assertFalse(deletable(self.pool))
        self.assertFalse(deletable(self.proc))
        self.assertTrue(deletable(self.root))

    def test_native_deletion_protects_flow_endpoints_until_flow_removed(self):
        source, target = self.node(), self.node(name="Destino")
        flow = create_flow(BPMNSequenceFlow, source, target, self.events)
        self.assertFalse(deletable(source))
        self.assertFalse(deletable(target))
        self.assertTrue(deletable(flow))
        self.assertTrue(deletable(self.root))
        with Transaction(self.events):
            flow.unlink()
        self.assertTrue(deletable(source))
        self.assertTrue(deletable(target))

    def test_native_lane_deletion_releases_assignment_but_blocks_association(self):
        lane = create_lane(self.proc, self.events)
        node = self.node(lane=lane)
        self.assertTrue(deletable(lane))
        annotation = self.node(BPMNTextAnnotation, text="Responsabilidad")
        association = create_flow(BPMNAssociation, annotation, lane, self.events)
        self.assertFalse(deletable(lane))
        self.assertFalse(deletable(annotation))
        with Transaction(self.events):
            association.unlink()
        self.assertTrue(deletable(lane))
        self.undo.clear_undo_stack()
        with Transaction(self.events):
            lane.unlink()
        self.assertIsNone(node.lane)
        self.undo.undo_transaction()
        self.assertEqual(node.lane.id, lane.id)
        self.assertIs(node.lane, self.factory.lookup(lane.id))

    def test_toolbox_pool_lane_and_node_semantic_membership(self):
        pool_item = self.visual(self.pool)
        lane_item = self.tool("bpmn-lane", pool_item)
        task_item = self.tool("bpmn-task", lane_item)
        self.assertIs(lane_item.subject.container, self.proc)
        self.assertIs(task_item.subject.container, self.proc)
        self.assertIs(task_item.subject.lane, lane_item.subject)
        self.assertIs(task_item.parent, lane_item)

    def test_multiple_pools_require_explicit_context_but_annotation_is_global(self):
        self.tool("bpmn-pool")
        self.assertIsNone(primary_process(self.diagram))
        task = self.tool("bpmn-task")
        self.assertTrue(task._bpmn_placement_error)
        annotation = self.tool("bpmn-annotation")
        self.assertIs(annotation.subject.container, self.root)
        self.assertFalse(hasattr(annotation, "_bpmn_placement_error"))

    def test_closed_pool_and_nested_lane_reject_creation(self):
        closed = self.tool("bpmn-pool-closed")
        with Transaction(self.events):
            self.diagram.update(list(self.diagram.get_all_items()))
        self.assertAlmostEqual(closed.height, 90)
        self.assertTrue(self.tool("bpmn-task", closed)._bpmn_placement_error)
        self.assertTrue(self.tool("bpmn-lane", closed)._bpmn_placement_error)
        lane = self.tool("bpmn-lane", self.visual(self.pool))
        self.assertTrue(self.tool("bpmn-lane", lane)._bpmn_placement_error)

    def test_move_between_lanes_keeps_process_and_is_undoable(self):
        pool_item = self.visual(self.pool)
        lane_a = self.tool("bpmn-lane", pool_item)
        lane_b = self.tool("bpmn-lane", pool_item)
        item = self.tool("bpmn-task", lane_a)
        self.undo.clear_undo_stack()
        with Transaction(self.events):
            drop(item, lane_b, 80, 30)
        self.assertIs(item.subject.lane, lane_b.subject)
        self.assertIs(item.subject.container, self.proc)
        self.undo.undo_transaction()
        self.assertIs(item.subject.lane, lane_a.subject)
        self.undo.redo_transaction()
        self.assertIs(item.subject.lane, lane_b.subject)

    def test_cross_process_drag_is_rejected_without_losing_lane(self):
        pool_item = self.visual(self.pool)
        lane = self.tool("bpmn-lane", pool_item)
        item = self.tool("bpmn-task", lane)
        other_pool = self.tool("bpmn-pool")
        other_lane = self.tool("bpmn-lane", other_pool)
        with Transaction(self.events):
            result = drop(item, other_lane, 40, 30)
        self.assertIsNone(result)
        self.assertIs(item.subject.container, self.proc)
        self.assertIs(item.subject.lane, lane.subject)
        self.assertIs(item.parent, lane)
        self.assertFalse(group(other_pool.subject, item.subject))

    def test_real_connector_creates_semantic_sequence_and_undo(self):
        a = self.visual(self.node(name="Origen"), 50, 50)
        b = self.visual(self.node(name="Destino"), 300, 50)
        self.undo.clear_undo_stack()
        line = self.line(a, b)
        flow_id = line.subject.id
        self.assertIs(line.subject.sourceRef, a.subject)
        self.assertIs(line.subject.targetRef, b.subject)
        self.assertIs(line.subject.container, self.proc)
        self.undo.undo_transaction()
        self.assertIsNone(self.factory.lookup(flow_id))
        self.undo.redo_transaction()
        self.assertIs(self.factory.lookup(flow_id).sourceRef, a.subject)

    def test_connector_rejects_sequence_to_start_and_between_pools(self):
        task = self.visual(self.node())
        start = self.visual(self.node(BPMNEvent, eventKind="START"), 280, 50)
        line = self.line(task, start)
        self.assertIsNone(line.subject)
        other = create_participant(self.root, self.events, name="Otro")
        node = create_node(BPMNTask, other.processRef, self.events, name="Otra tarea")
        target = self.visual(node, 450, 50)
        line = self.line(task, target)
        self.assertIsNone(line.subject)

    def test_message_connector_and_second_message_rejected(self):
        customer = self.tool("bpmn-pool-closed")
        event = self.node(BPMNEvent, "Corrección recibida", eventKind="INTERMEDIATE", eventDefinition="MESSAGE", eventDirection="CATCH")
        event_item = self.visual(event, 100, 200)
        line = self.line(customer, event_item, view.BPMNMessageFlowItem)
        self.assertIsInstance(line.subject, BPMNMessageFlow)
        self.assertIs(line.subject.container, self.root)
        another = self.line(customer, event_item, view.BPMNMessageFlowItem)
        self.assertIsNone(another.subject)

    def test_message_start_accepts_multiple_incoming_connectors(self):
        customer = self.tool("bpmn-pool-closed")
        event = self.node(BPMNEvent, "Pedido recibido", eventKind="START", eventDefinition="MESSAGE")
        event_item = self.visual(event, 100, 200)
        first = self.line(customer, event_item, view.BPMNMessageFlowItem)
        second = self.line(customer, event_item, view.BPMNMessageFlowItem)
        self.assertIsInstance(first.subject, BPMNMessageFlow)
        self.assertIsInstance(second.subject, BPMNMessageFlow)
        self.assertIsNot(first.subject, second.subject)

    def test_conditional_default_reconnection_rejects_parallel_source(self):
        source, target = self.node(), self.node(name="Destino")
        gateway = self.node(BPMNGateway, gatewayKind="PARALLEL")
        a, b, g = self.visual(source), self.visual(target, 300, 30), self.visual(gateway, 500, 30)
        flow = create_flow(BPMNSequenceFlow, source, target, self.events, flowKind="DEFAULT")
        line = self.visual(flow)
        self.assertFalse(view.BPMNConnector(g, line).allow(line.tail, g.ports()[0]))

    def test_multiple_presentations_block_retargeting(self):
        source, target, other = self.node(), self.node(name="Destino"), self.node(name="Otro")
        a, b, c = self.visual(source), self.visual(target, 300, 30), self.visual(other, 500, 30)
        line = self.line(a, b)
        with Transaction(self.events):
            duplicate = self.diagram.create(view.BPMNSequenceFlowItem, subject=line.subject)
        self.assertFalse(view.BPMNConnector(c, line).allow(line.head, c.ports()[0]))
        self.assertTrue(view.BPMNConnector(b, line).allow(line.head, b.ports()[0]))

    def test_drop_existing_flow_repairs_detached_endpoint(self):
        a, b = self.visual(self.node()), self.visual(self.node(name="Destino"), 300, 30)
        line = self.line(a, b)
        flow = line.subject
        with Transaction(self.events):
            ConnectorAspect(line, line.head, self.diagram.connections).disconnect()
        self.assertIsNone(self.diagram.connections.get_connection(line.head))
        with Transaction(self.events):
            repaired = view.drop_flow(flow, self.diagram)
        self.assertIs(repaired, line)
        self.assertIs(self.diagram.connections.get_connection(line.head).connected, b)

    def test_association_can_connect_annotation_to_lane(self):
        lane = create_lane(self.proc, self.events)
        annotation = self.node(BPMNTextAnnotation, text="Criterio de revisión")
        line = self.line(self.visual(annotation), self.visual(lane, 30, 200), view.BPMNAssociationItem)
        self.assertIsInstance(line.subject, BPMNAssociation)
        self.assertIs(line.subject.container, self.root)

    def test_roundtrip_keeps_native_connections_and_labels(self):
        a, b = self.visual(self.node()), self.visual(self.node(name="Destino"), 300, 30)
        line = self.line(a, b)
        with Transaction(self.events):
            line.subject.flowKind = "CONDITIONAL"
            line.subject.conditionExpression = "Cantidad > 0"
        stream = io.StringIO(); save(stream, self.factory)
        self.assertIn("modelinglanguage/BPMN", stream.getvalue())
        other = ElementFactory()
        try:
            load(io.StringIO(stream.getvalue()), other, self.language)
            restored = other.lookup(line.id)
            self.assertEqual(restored.flow_label(), "Cantidad > 0")
            self.assertIs(restored.subject.sourceRef, other.lookup(a.subject.id))
            self.assertIsNotNone(restored.diagram.connections.get_connection(restored.head))
            self.assertIsNotNone(restored.diagram.connections.get_connection(restored.tail))
        finally:
            other.shutdown()

    def test_shallow_copy_reuses_subject_and_pool_deep_copy_remaps_process(self):
        pool_item = self.visual(self.pool)
        lane = self.tool("bpmn-lane", pool_item)
        task = self.tool("bpmn-task", lane)
        data = copy_full([pool_item], self.factory.lookup)
        with Transaction(self.events):
            linked = paste_link(data, self.diagram)
        self.assertTrue(any(i.subject is self.pool for i in linked))
        with Transaction(self.events):
            pasted = paste_full(data, self.diagram)
        new_pool = next(i.subject for i in pasted if isinstance(i.subject, BPMNParticipant))
        self.assertIsNot(new_pool, self.pool)
        self.assertIsNot(new_pool.processRef, self.proc)
        self.assertTrue(any(isinstance(n, BPMNTask) for n in new_pool.processRef.ownedElements))
        self.assertFalse([d for d in validate(self.root) if d.severity == "error"])

    def test_missing_flow_copy_dependency_rolls_back(self):
        line = self.line(self.visual(self.node()), self.visual(self.node(name="Destino"), 300, 30))
        data = copy_full([line], self.factory.lookup)
        events = EventManager()
        factory = ElementFactory(events, self.dispatcher)
        manager = UndoManager(events, factory)
        try:
            _, target_diagram = create_collaboration(factory, events)
            before = factory.size()
            with self.assertRaises(view.BPMNCopyError):
                with Transaction(events):
                    paste_full(data, target_diagram)
            self.assertEqual(factory.size(), before)
        finally:
            manager.shutdown(); factory.shutdown()

    def test_native_png_svg_export_supported_glyphs(self):
        with Transaction(self.events):
            self._export_native_glyphs()

    def _export_native_glyphs(self):
        sheet = self.factory.style_sheet or self.factory.create(StyleSheet)
        sheet.styleSheet = "diagram { background-color: white; color: #172129; }"
        pool_item = self.visual(self.pool, 30, 30)
        pool_item.width, pool_item.height = 940, 380
        lane_a = self.tool("bpmn-lane", pool_item)
        lane_a.matrix.set(1, 0, 0, 1, 38, 10)
        lane_a.width, lane_a.height = 890, 170
        lane_b = self.tool("bpmn-lane", pool_item)
        lane_b.subject.name = "Bodega"
        lane_b.matrix.set(1, 0, 0, 1, 38, 185)
        lane_b.width, lane_b.height = 890, 180
        start = self.tool("bpmn-start", lane_a); start.subject.eventDefinition = "MESSAGE"
        task = self.tool("bpmn-task", lane_a); task.subject.name = "Validar pedido"
        decision = self.tool("bpmn-exclusive", lane_a)
        sub = self.tool("bpmn-subprocess", lane_b); sub.subject.name = "Preparar pedido"
        end = self.tool("bpmn-end", lane_b)
        for item, x, y in ((start, 70, 45), (task, 180, 30), (decision, 400, 40), (sub, 460, 40), (end, 700, 55)):
            item.matrix.set(1, 0, 0, 1, x, y)
        for source, target in ((start, task), (task, decision), (decision, sub), (sub, end)):
            self.line(source, target)
        closed = self.tool("bpmn-pool-closed")
        closed.subject.name = "Cliente"
        closed.matrix.set(1, 0, 0, 1, 100, -140)
        self.line(closed, start, view.BPMNMessageFlowItem)
        annotation = self.tool("bpmn-annotation")
        annotation.subject.text = "Verificar cantidades y referencias"
        annotation.matrix.set(1, 0, 0, 1, 520, -110)
        self.line(task, annotation, view.BPMNAssociationItem)
        output = Path(os.environ["GAPHOR_BPMN_TEST_OUTPUT"])
        self.diagram.update(list(self.diagram.get_all_items()))
        save_png(str(output / "bpmn-diagram.png"), self.diagram)
        save_svg(str(output / "bpmn-diagram.svg"), self.diagram)
        stream = io.StringIO(); save(stream, self.factory)
        (output / "bpmn-diagram.gaphor").write_text(stream.getvalue(), encoding="utf-8")
        self.assertGreater((output / "bpmn-diagram.png").stat().st_size, 100)
        self.assertIn("<svg", (output / "bpmn-diagram.svg").read_text(encoding="utf-8"))

    def test_render_event_variants_and_parallel_gateway(self):
        configurations = (("START", "NONE", "CATCH"), ("START", "MESSAGE", "CATCH"),
                          ("START", "TIMER", "CATCH"), ("INTERMEDIATE", "NONE", "THROW"),
                          ("INTERMEDIATE", "MESSAGE", "CATCH"), ("INTERMEDIATE", "MESSAGE", "THROW"),
                          ("INTERMEDIATE", "TIMER", "CATCH"), ("END", "NONE", "THROW"),
                          ("END", "MESSAGE", "THROW"))
        with Transaction(self.events):
            sheet = self.factory.style_sheet or self.factory.create(StyleSheet)
            sheet.styleSheet = "diagram { background-color: white; color: #172129; }"
            for index, (kind, definition, direction) in enumerate(configurations):
                subject = self.node(BPMNEvent, f"{kind}\n{definition} {direction}", eventKind=kind, eventDefinition=definition, eventDirection=direction)
                self.visual(subject, 30 + (index % 3) * 220, 30 + (index // 3) * 150)
            self.visual(self.node(BPMNGateway, "Paralela", gatewayKind="PARALLEL"), 690, 30)
            self.visual(self.node(BPMNGateway, "Exclusiva", gatewayKind="EXCLUSIVE"), 690, 200)
            output = Path(os.environ["GAPHOR_BPMN_TEST_OUTPUT"])
            save_png(str(output / "bpmn-glyphs.png"), self.diagram)
            save_svg(str(output / "bpmn-glyphs.svg"), self.diagram)
        self.assertGreater((output / "bpmn-glyphs.png").stat().st_size, 100)

    def test_event_ports_follow_circle_and_gateway_ports_follow_diamond(self):
        start = self.visual(self.node(BPMNEvent, eventKind="START"), 50, 50)
        target = self.visual(self.node(), 300, 250)
        line = self.line(start, target)
        sx, sy = start.matrix_i2c.inverse().transform_point(*line.tail.pos)
        self.assertAlmostEqual(((sx - 22) ** 2 + (sy - 22) ** 2) ** .5, 20, delta=.5)
        gateway = self.visual(self.node(BPMNGateway), 500, 80)
        line2 = self.line(target, gateway)
        gx, gy = gateway.matrix_i2c.inverse().transform_point(*line2.head.pos)
        self.assertAlmostEqual(abs(gx - 27) + abs(gy - 27), 27, delta=.1)
