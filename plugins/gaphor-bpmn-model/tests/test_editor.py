from types import SimpleNamespace
from unittest.mock import patch
import unittest

from gi.repository import Gio, GLib, Gtk
from gaphor import UML
from gaphor.core import Transaction
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import ElementFactory
from gaphor.core.modeling.elementdispatcher import ElementDispatcher
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.services.undomanager import UndoManager

from gaphor_bpmn_model import model
from gaphor_bpmn_model.editor import BPMNEditor, read_text
from gaphor_bpmn_model.language import BPMNLanguage
from gaphor_bpmn_model.operations import (
    create_collaboration, create_flow, create_lane, create_node, create_participant,
    snapshot, update_element,
)
from gaphor_bpmn_model.service import BPMNPropertyPage, BPMNService, selected_collaboration


class EditorTests(unittest.TestCase):
    def setUp(self):
        Gtk.init()
        self.events = EventManager()
        self.language = ModelingLanguageService(self.events)
        self.language._modeling_languages["BPMN"] = BPMNLanguage()
        self.dispatcher = ElementDispatcher(self.events, self.language)
        self.model = ElementFactory(self.events, self.dispatcher)
        self.undo = UndoManager(self.events, self.model)
        self.root, self.diagram = create_collaboration(self.model, self.events)
        self.pool = create_participant(self.root, self.events, "Exotic")
        self.process = self.pool.processRef
        self.windows, self.services = [], []

    def tearDown(self):
        for window in self.windows:
            window.cancel()
        for service in self.services:
            service.shutdown()
        context = GLib.MainContext.default()
        for _ in range(100):
            if not context.pending():
                break
            context.iteration(False)
        self.undo.shutdown()
        self.model.shutdown()
        self.dispatcher.shutdown()
        self.language.shutdown()

    def node(self, cls=model.BPMNTask, **attributes):
        return create_node(cls, self.process, self.events, name="Validar pedido", **attributes)

    def editor(self, subject, **kwargs):
        editor = BPMNEditor(None, subject, self.events, **kwargs)
        self.windows.append(editor)
        return editor

    def service(self):
        service = BPMNService(SimpleNamespace(window=None), SimpleNamespace(menu=Gio.Menu.new()),
                              self.events, self.model,
                              SimpleNamespace(get_current_diagram=lambda: self.diagram))
        self.services.append(service)
        return service

    def test_cancel_does_not_change_model(self):
        node = self.node()
        before = snapshot(node)
        editor = self.editor(node)
        editor.name.set_text("Borrador")
        editor.documentation.get_buffer().set_text("Sin guardar")
        editor.cancel()
        self.assertEqual(snapshot(node), before)

    def test_save_is_one_undoable_transaction(self):
        node = self.node()
        before = snapshot(node)
        editor = self.editor(node)
        editor.name.set_text("Comprobar disponibilidad")
        editor.documentation.get_buffer().set_text("Responsable: atención al cliente")
        self.undo.clear_undo_stack()
        self.assertTrue(editor.save(), editor.error.get_text())
        after = snapshot(node)
        self.assertTrue(editor.finished)
        self.undo.undo_transaction()
        self.assertEqual(snapshot(node), before)
        self.undo.redo_transaction()
        self.assertEqual(snapshot(node), after)

    def test_stale_draft_cannot_overwrite_native_edit(self):
        node = self.node()
        editor = self.editor(node)
        update_element(node, {"name": "Cambio externo"}, self.events)
        editor.name.set_text("Borrador viejo")
        self.assertFalse(editor.save())
        self.assertEqual(node.name, "Cambio externo")
        self.assertIn("cambió", editor.error.get_text())
        self.assertFalse(editor.finished)

    def test_event_change_respects_existing_connections(self):
        task = self.node()
        end = self.node(model.BPMNEvent, eventKind="END", eventDirection="THROW")
        flow = create_flow(model.BPMNSequenceFlow, task, end, self.events)
        before = snapshot(end)
        editor = self.editor(end)
        editor.controls["event"].set_active_id("START|NONE|CATCH")
        self.assertFalse(editor.save())
        self.assertEqual(snapshot(end), before)
        self.assertIs(flow.targetRef, end)
        self.assertFalse(editor.finished)

    def test_event_options_are_valid_combinations(self):
        event = self.node(model.BPMNEvent)
        editor = self.editor(event)
        editor.controls["event"].set_active_id("INTERMEDIATE|TIMER|CATCH")
        self.assertTrue(editor.save(), editor.error.get_text())
        self.assertEqual((event.eventKind, event.eventDefinition, event.eventDirection),
                         ("INTERMEDIATE", "TIMER", "CATCH"))

    def test_only_lanes_of_same_process_are_offered(self):
        own_lane = create_lane(self.process, self.events, "Atención")
        foreign = create_participant(self.root, self.events, "Proveedor")
        foreign_lane = create_lane(foreign.processRef, self.events, "Ventas")
        node = self.node()
        editor = self.editor(node)
        selector = editor.controls["lane"]
        selector.set_active_id(foreign_lane.id)
        self.assertNotEqual(selector.get_active_id(), foreign_lane.id)
        selector.set_active_id(own_lane.id)
        self.assertTrue(editor.save(), editor.error.get_text())
        self.assertIs(node.lane, own_lane)
        self.assertIs(model.scope(node), self.process)

    def test_annotation_unicode_and_multiline(self):
        note = self.node(model.BPMNTextAnnotation, text="Inicial")
        editor = self.editor(note)
        editor.controls["text"].get_buffer().set_text("Revisar dirección\nEntrega: Bogotá — lote ①")
        self.assertTrue(editor.save(), editor.error.get_text())
        self.assertIn("Bogotá", note.text)
        self.assertIn("\n", note.text)

    def test_callback_failure_rolls_back_entire_edit(self):
        node = self.node()
        before = snapshot(node)
        def fail(_element):
            raise ValueError("No se pudo actualizar la vista")
        editor = self.editor(node, after_save=fail)
        editor.name.set_text("Cambio no confirmado")
        self.assertFalse(editor.save())
        self.assertEqual(snapshot(node), before)
        self.assertFalse(editor.finished)

    def test_closed_pool_can_be_opened_and_undo_restores_it(self):
        pool = create_participant(self.root, self.events, "Cliente", is_closed=True)
        editor = self.editor(pool)
        editor.controls["isClosed"].set_active(False)
        self.undo.clear_undo_stack()
        self.assertTrue(editor.save(), editor.error.get_text())
        self.assertFalse(pool.isClosed)
        self.assertIsNotNone(pool.processRef)
        self.undo.undo_transaction()
        self.assertTrue(pool.isClosed)
        self.assertIsNone(pool.processRef)

    def test_nonempty_pool_cannot_be_closed(self):
        self.node()
        editor = self.editor(self.pool)
        editor.controls["isClosed"].set_active(True)
        self.assertFalse(editor.save())
        self.assertFalse(self.pool.isClosed)
        self.assertFalse(editor.finished)

    def test_drafts_from_two_editors_are_independent(self):
        left, right = self.node(), self.node()
        a, b = self.editor(left), self.editor(right)
        a.name.set_text("A")
        b.name.set_text("B")
        self.assertTrue(a.save())
        b.cancel()
        self.assertEqual(left.name, "A")
        self.assertEqual(right.name, "Validar pedido")

    def test_editor_is_resizable_and_empty_documentation_is_text(self):
        editor = self.editor(self.node())
        self.assertTrue(editor.get_resizable())
        self.assertEqual(read_text(editor.documentation), "")

    def test_service_menu_lifecycle_and_property_page(self):
        service = self.service()
        self.assertTrue(service.compatible)
        menu = service.tools_menu.exotic_custom_tools_menu
        self.assertEqual(menu.get_n_items(), 1)
        page = BPMNPropertyPage(self.node(), self.events)
        self.assertIsNotNone(page.construct())
        service.shutdown()
        service.shutdown()
        self.assertEqual(menu.get_n_items(), 0)
        self.assertIsNone(page.construct())

    def test_service_new_diagram_reuses_selected_collaboration(self):
        service = self.service()
        service.focused = self.pool
        created = service.new_diagram()
        self.assertIs(created.element, self.root)
        self.assertIs(selected_collaboration(created), self.root)

    def test_service_creates_diagram_inside_selected_package(self):
        with Transaction(self.events):
            package = self.model.create(UML.Package)
            package.name = "Ingreso materiales"
        service = self.service()
        service.focused = package
        created = service.new_diagram()
        root = selected_collaboration(created)
        self.assertIs(created.element, package)
        self.assertIs(root.folder, package)
        self.assertIs(created.bpmnCollaboration, root)
        self.assertIn(root, package.ownedMember)

    def test_service_reuses_folder_collaboration_without_moving_diagram(self):
        with Transaction(self.events):
            package = self.model.create(UML.Package)
            children = self.model.create(UML.Package)
            children.nestingPackage = package
            self.root.folder = children
            self.diagram.element = package
            self.diagram.bpmnCollaboration = self.root
        service = self.service()
        service.focused = self.diagram
        before = len(list(self.model.select(model.BPMNCollaboration)))
        created = service.new_diagram()
        self.assertIs(created.element, package)
        self.assertIs(selected_collaboration(created), self.root)
        self.assertEqual(len(list(self.model.select(model.BPMNCollaboration))), before)
        service.focused = created
        with patch.object(service, "_show_report"):
            self.assertIsNotNone(service.validate_diagram())

    def test_service_validation_returns_structured_diagnostics(self):
        service = self.service()
        self.node()
        with patch.object(service, "_show_report") as report:
            result = service.validate_diagram()
        self.assertTrue(any(d.code == "no-incoming-sequence" for d in result))
        self.assertIn("no comprueba", report.call_args.args[0].lower())

    def test_service_shutdown_does_not_disable_other_session(self):
        first = self.service()
        # A second event manager is sufficient to check the page/service registry.
        other_events = EventManager()
        other = BPMNService(SimpleNamespace(window=None), SimpleNamespace(menu=Gio.Menu.new()),
                            other_events, self.model, SimpleNamespace(get_current_diagram=lambda: self.diagram))
        self.services.append(other)
        first.shutdown()
        self.assertIsNotNone(BPMNPropertyPage(self.pool, other_events).construct())

    def test_participant_deletion_requires_confirmation_and_cancel_preserves_it(self):
        service = self.service()
        service.focused = self.pool
        before = self.model.size()
        with patch.object(Gtk.Window, "present"):
            window = service.delete_participant()
        actions = window.get_child().get_last_child()
        actions.get_first_child().emit("clicked")
        self.assertIsNone(service.delete_window)
        self.assertEqual(self.model.size(), before)
        self.assertIs(self.model.lookup(self.pool.id), self.pool)

    def test_confirmed_participant_deletion_and_contents_are_undoable(self):
        node = self.node()
        service = self.service()
        service.focused = self.pool
        with patch.object(Gtk.Window, "present"):
            window = service.delete_participant()
        self.undo.clear_undo_stack()
        window.get_child().get_last_child().get_last_child().emit("clicked")
        self.assertIsNone(self.model.lookup(self.pool.id))
        self.assertIsNone(self.model.lookup(node.id))
        self.undo.undo_transaction()
        restored_pool = self.model.lookup(self.pool.id)
        restored_node = self.model.lookup(node.id)
        restored_process = self.model.lookup(self.process.id)
        self.assertEqual(restored_pool.name, "Exotic")
        self.assertEqual(restored_node.name, "Validar pedido")
        self.assertIs(restored_pool.processRef, restored_process)
        self.assertIs(restored_node.container, restored_process)
