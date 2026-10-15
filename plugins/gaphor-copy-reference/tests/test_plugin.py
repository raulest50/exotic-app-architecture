import io
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from gi.repository import Gdk, Gio, Gtk
from gaphor import UML
from gaphor.core import Transaction, event_handler
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import ElementFactory
from gaphor.core.modeling.elementdispatcher import ElementDispatcher
from gaphor.event import Notification
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.services.undomanager import UndoManager
from gaphor.storage.save import save
from gaphor.UML.classes.package import PackageItem
from gaphor.UML.classes.component import ComponentItem
from gaphor.UML.deployments.artifact import ArtifactItem
from gaphor.ui import modelbrowser, diagrampage

import gaphor_copy_reference as plugin
from gaphor_copy_reference.paths import ReferenceError, diagram_path, element_name, tree_path
from helpers import action_target, clipboard_text, entries


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        Gtk.init()
        self.events = EventManager()
        self.language = ModelingLanguageService(self.events)
        self.dispatcher = ElementDispatcher(self.events, self.language)
        self.model = ElementFactory(self.events, self.dispatcher)
        self.undo = UndoManager(self.events, self.model)
        self.native_tree = modelbrowser.popup_model
        self.native_controller = diagrampage.context_menu_controller
        self.window = Gtk.Window()
        self.services = []
        self.notifications = []
        self.events.subscribe(self.on_notification)
        with Transaction(self.events):
            self.diagram = self.model.create(UML.ComponentDiagram)
            self.diagram.name = "Temporal"
            self.outer = self.package("Productos")
            self.basic = self.package("Basic", self.outer)
            self.components = self.package("componentes", self.basic)
            self.element = self.model.create(UML.Artifact)
            self.element.name = "FichaTecnicaMaterialCard.tsx"
            self.element.package = self.components.subject
            self.item = self.diagram.create(ArtifactItem, subject=self.element, parent=self.components)
        self.current = self.diagram
        self.undo.clear_undo_stack()

    @event_handler(Notification)
    def on_notification(self, event):
        self.notifications.append(event.message)

    def tearDown(self):
        for service in self.services:
            service.shutdown()
        self.window.destroy()
        self.undo.shutdown()
        self.model.shutdown()
        self.dispatcher.shutdown()
        self.language.shutdown()

    def package(self, name, parent=None):
        subject = self.model.create(UML.Package)
        subject.name = name
        return self.diagram.create(PackageItem, subject=subject, parent=parent)

    def service(self):
        service = plugin.CopyReferenceService(
            SimpleNamespace(window=self.window), self.events, self.model,
            SimpleNamespace(get_current_diagram=lambda: self.current),
        )
        self.services.append(service)
        return service

    def target(self, service, tree=False, element=None):
        menu = Gio.Menu.new()
        service.extend_menu(menu, element or self.element,
                            None if tree else self.item, None if tree else self.diagram)
        return action_target(menu, "Copiar ruta relativa")

    def snapshot(self):
        output = io.StringIO()
        save(output, self.model)
        return output.getvalue()

    def test_nested_path_includes_outer_package_and_extension(self):
        self.assertEqual(diagram_path(self.item, self.diagram, self.model),
                         "Productos/Basic/componentes/FichaTecnicaMaterialCard.tsx")
        self.assertEqual(diagram_path(self.basic, self.diagram, self.model), "Productos/Basic")

    def test_model_ancestors_do_not_enter_graphical_path(self):
        with Transaction(self.events):
            organizer = self.model.create(UML.Package)
            organizer.name = "elements"
            self.outer.subject.nestingPackage = organizer
        self.assertNotIn("elements", diagram_path(self.item, self.diagram, self.model))

    def test_graphical_elements_package_is_not_filtered(self):
        with Transaction(self.events):
            self.basic.subject.name = "elements"
        self.assertEqual(diagram_path(self.item, self.diagram, self.model),
                         "Productos/elements/componentes/FichaTecnicaMaterialCard.tsx")

    def test_uncontained_element_ignores_semantic_owner(self):
        with Transaction(self.events):
            self.item.parent = None
        self.assertEqual(diagram_path(self.item, self.diagram, self.model), self.element.name)

    def test_non_package_containers_do_not_add_path_segments(self):
        with Transaction(self.events):
            component = self.model.create(UML.Component)
            component.name = "Panel"
            container = self.diagram.create(ComponentItem, subject=component, parent=self.components)
            self.item.parent = container
        self.assertEqual(diagram_path(self.item, self.diagram, self.model),
                         "Productos/Basic/componentes/FichaTecnicaMaterialCard.tsx")

    def test_spaces_unicode_and_case_preserved(self):
        with Transaction(self.events):
            self.outer.subject.name = "Producción 日本"
            self.element.name = "Ficha técnica Á.TSX"
        self.assertEqual(diagram_path(self.item, self.diagram, self.model),
                         "Producción 日本/Basic/componentes/Ficha técnica Á.TSX")

    def test_multiple_outer_packages_use_correct_one(self):
        with Transaction(self.events):
            other = self.package("Otro")
            self.item.parent = other
        self.assertEqual(diagram_path(self.item, self.diagram, self.model), "Otro/" + self.element.name)

    def test_tree_repeated_same_path_is_unambiguous(self):
        with Transaction(self.events):
            self.diagram.create(ArtifactItem, subject=self.element, parent=self.components)
        self.assertEqual(tree_path(self.element, self.diagram, self.model),
                         diagram_path(self.item, self.diagram, self.model))

    def test_tree_different_paths_requires_figure(self):
        with Transaction(self.events):
            self.diagram.create(ArtifactItem, subject=self.element, parent=self.basic)
        with self.assertRaisesRegex(ReferenceError, "varias rutas"):
            tree_path(self.element, self.diagram, self.model)

    def test_tree_missing_diagram_or_presentation(self):
        with self.assertRaisesRegex(ReferenceError, "Abre un diagrama"):
            tree_path(self.element, None, self.model)
        with Transaction(self.events):
            other = self.model.create(UML.ComponentDiagram)
        with self.assertRaisesRegex(ReferenceError, "no aparece"):
            tree_path(self.element, other, self.model)

    def test_unnamed_or_deleted_element_and_unnamed_parent(self):
        with Transaction(self.events):
            self.basic.subject.name = ""
        with self.assertRaisesRegex(ReferenceError, "nombre"):
            diagram_path(self.item, self.diagram, self.model)
        with Transaction(self.events):
            self.element.name = "  "
        with self.assertRaisesRegex(ReferenceError, "nombre"):
            element_name(self.element, self.model)
        with Transaction(self.events):
            self.element.unlink()
        with self.assertRaisesRegex(ReferenceError, "disponible"):
            element_name(self.element, self.model)

    def test_clipboard_plain_text_and_notification(self):
        service = self.service()
        target = self.target(service)
        self.assertTrue(service._copy(target, path=True))
        self.assertEqual(clipboard_text(self.window), "Productos/Basic/componentes/" + self.element.name)
        service.copy_name(target)
        self.assertEqual(clipboard_text(self.window), self.element.name)
        self.assertEqual(self.notifications, ["Copiado", "Copiado"])

    def test_ambiguous_path_preserves_clipboard(self):
        service = self.service()
        target = self.target(service, tree=True)
        self.window.get_clipboard().set_content(Gdk.ContentProvider.new_for_value("conservar"))
        with Transaction(self.events):
            self.diagram.create(ArtifactItem, subject=self.element)
        self.assertFalse(service._copy(target, path=True))
        self.assertEqual(clipboard_text(self.window), "conservar")
        self.assertIn("varias rutas", self.notifications[-1])

    def test_tree_name_without_active_diagram(self):
        service = self.service()
        target = self.target(service, tree=True)
        self.current = None
        self.assertTrue(service._copy(target, path=False))
        self.assertFalse(service._copy(target, path=True))
        self.assertEqual(clipboard_text(self.window), self.element.name)

    def test_menu_target_resolves_renames_and_reparenting_when_invoked(self):
        service = self.service()
        target = self.target(service)
        with Transaction(self.events):
            self.element.name = "Nueva.ts"
            self.outer.subject.name = "Renombrado"
            self.item.parent = self.outer
        self.assertEqual(service._resolve(target, True), "Renombrado/Nueva.ts")

    def test_deleted_figure_rejected_but_tree_name_remains_available(self):
        service = self.service()
        target = self.target(service)
        with Transaction(self.events):
            self.item.unlink()
        with self.assertRaisesRegex(ReferenceError, "figura"):
            service._resolve(target, False)
        self.assertEqual(service._resolve(self.target(service, tree=True), False), self.element.name)

    def test_removed_element_and_changed_diagram_rejected(self):
        service = self.service()
        target = self.target(service)
        self.current = None
        with self.assertRaisesRegex(ReferenceError, "activo cambió"):
            service._resolve(target, True)
        self.current = self.diagram
        with Transaction(self.events):
            self.element.unlink()
        with self.assertRaisesRegex(ReferenceError, "disponible"):
            service._resolve(target, False)

    def test_session_token_and_invalid_targets_rejected(self):
        service = self.service()
        target = json.loads(self.target(service))
        target["session"] = "another-project"
        for payload in (json.dumps(target), "not json", "[]", "null", "{}"):
            with self.subTest(payload=payload), self.assertRaises(ReferenceError):
                service._resolve(payload, True)

    def test_original_tree_entries_preserved_and_no_duplicate_actions(self):
        original = list(entries(self.native_tree(self.element, self.language)))
        service = self.service()
        menu = modelbrowser.popup_model(self.element, self.language)
        service.extend_menu(menu, self.element)
        actual = list(entries(menu))
        self.assertEqual([(a,b) for a,b,_ in actual[:-2]], [(a,b) for a,b,_ in original])
        self.assertEqual([a for a,_,_ in actual[-2:]], ["Copiar nombre", "Copiar ruta relativa"])
        service.shutdown()
        self.assertEqual([(a,b) for a,b,_ in entries(menu)], [(a,b) for a,b,_ in original])
        self.assertIs(modelbrowser.popup_model, self.native_tree)
        self.assertIs(diagrampage.context_menu_controller, self.native_controller)

    def test_unnamed_element_has_only_original_menu(self):
        self.service()
        with Transaction(self.events):
            self.element.name = ""
        self.assertNotIn("Copiar nombre", [e[0] for e in entries(modelbrowser.popup_model(self.element, self.language))])

    def test_stopped_service_cannot_copy_and_disconnects_controller(self):
        service = self.service()
        target = self.target(service)
        popover = Gtk.PopoverMenu()
        controller = diagrampage.context_menu_controller(popover, self.diagram)
        handler, _popover, _diagram = service.controllers[controller]
        service.shutdown()
        self.assertFalse(controller.handler_is_connected(handler))
        self.assertFalse(service._copy(target, False))
        service.shutdown()

    def test_no_event_or_wrong_view_has_no_menu_effect(self):
        service = self.service()
        menu = Gio.Menu.new()
        context = SimpleNamespace(get_menu_model=lambda: menu)
        controller = SimpleNamespace(get_last_event=lambda: None)
        service.on_context_pressed(controller, 1, 0, 0, context, self.diagram)
        controller.get_last_event = lambda: SimpleNamespace(triggers_context_menu=lambda: True)
        controller.get_widget = lambda: None
        service.on_context_pressed(controller, 1, 0, 0, context, self.diagram)
        self.assertEqual(menu.get_n_items(), 0)

    def test_copy_and_menus_do_not_modify_serialized_model(self):
        before = self.snapshot()
        service = self.service()
        service.copy_path(self.target(service))
        modelbrowser.popup_model(self.element, self.language)
        service.shutdown()
        self.assertEqual(self.snapshot(), before)

    def test_unsupported_version_does_not_patch_native_menus(self):
        with patch.object(plugin, "version", return_value="9.0.0"):
            service = self.service()
        self.assertFalse(service.compatible)
        self.assertIs(modelbrowser.popup_model, self.native_tree)
