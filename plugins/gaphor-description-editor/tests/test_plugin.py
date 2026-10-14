import io
import os
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from gi.repository import Gdk, GLib, Gtk

from gaphor import UML
from gaphor.core import Transaction
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import ElementFactory
from gaphor.core.modeling.elementdispatcher import ElementDispatcher
from gaphor.core.modeling.event import ModelReady
from gaphor.diagram.event import DiagramOpened, DiagramSelectionChanged
from gaphor.diagram.tools import textedit
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.services.undomanager import UndoManager
from gaphor.storage.load import load
from gaphor.storage.save import save
from gaphor.UML.classes.component import ComponentItem
from gaphor.ui.event import ModelSelectionChanged

import gaphor_description_editor as plugin
from gaphor_description_editor.model import (
    DocumentationError, definition, read_description, save_documentation, save_properties,
)


def drain_events():
    context = GLib.MainContext.default()
    while context.pending():
        context.iteration(False)


class PluginTests(unittest.TestCase):
    def setUp(self):
        Gtk.init()
        self.events = EventManager()
        self.language = ModelingLanguageService(self.events)
        self.dispatcher = ElementDispatcher(self.events, self.language)
        self.model = ElementFactory(self.events, self.dispatcher)
        self.undo = UndoManager(self.events, self.model)
        with Transaction(self.events):
            self.component = self.model.create(UML.Component)
            self.component.name = "Componente temporal"
            self.component.note = "Nota original áéíóú"
        self.undo.clear_undo_stack()
        self.services = []
        self.windows = []

    def tearDown(self):
        for window in self.windows:
            window.cancel()
        for service in self.services:
            service.shutdown()
        drain_events()
        self.undo.shutdown()
        self.model.shutdown()
        self.dispatcher.shutdown()
        self.language.shutdown()

    def service(self, events=None, model=None):
        service = plugin.DescriptionEditor(
            SimpleNamespace(window=None), Mock(), events or self.events,
            model or self.model, Mock(),
        )
        self.services.append(service)
        return service

    def window(self):
        window = plugin.DocumentationWindow(None, self.component, self.events, Mock())
        self.windows.append(window)
        return window

    def test_read_and_cancel_have_no_side_effects(self):
        before = self.model.size()
        window = self.window()
        window.description_buffer.set_text("Sin guardar")
        window.note_buffer.set_text("Sin guardar tampoco")
        window.cancel()
        self.assertEqual(self.model.size(), before)
        self.assertEqual(read_description(self.component), "")
        self.assertEqual(self.component.note, "Nota original áéíóú")

    def test_save_both_fields_and_undo_redo_once(self):
        before = self.model.size()
        window = self.window()
        description = "Primera línea: intención & <contrato>\nSegunda línea.\n" * 500
        window.description_buffer.set_text(description)
        window.note_buffer.set_text("Otra nota\nIndependiente")
        self.assertTrue(window.save())
        self.assertEqual(read_description(self.component), description)
        self.assertEqual(self.component.note, "Otra nota\nIndependiente")
        self.undo.undo_transaction()
        self.assertEqual(read_description(self.component), "")
        self.assertEqual(self.component.note, "Nota original áéíóú")
        self.assertEqual(self.model.size(), before)
        self.undo.redo_transaction()
        self.assertEqual(read_description(self.component), description)
        self.assertEqual(self.component.note, "Otra nota\nIndependiente")

    def test_note_only_creates_no_profile(self):
        before = self.model.size()
        save_documentation(self.component, "", "Nota nueva", self.events)
        self.assertEqual(self.model.size(), before)
        self.assertIsNone(definition(self.model).profile)

    def test_repeated_edits_reuse_definition_slots_and_identifiers(self):
        save_documentation(self.component, "Uno", self.component.note, self.events)
        original_ids = {e.id for e in self.model}
        for value in ("Dos", "Tres", ""):
            save_documentation(self.component, value, self.component.note, self.events)
            self.assertEqual(read_description(self.component), value)
            self.assertEqual({e.id for e in self.model}, original_ids)
        self.assertEqual(self.component.note, "Nota original áéíóú")
        self.assertFalse(save_documentation(self.component, "", self.component.note, self.events))

    def test_supported_types_reuse_one_profile(self):
        for cls in (UML.Component, UML.Artifact, UML.Package, UML.Dependency):
            with self.subTest(cls=cls.__name__):
                with Transaction(self.events):
                    subject = self.model.create(cls)
                save_documentation(subject, f"Descripción de {cls.__name__}", "Nota", self.events)
                spec = definition(self.model)
                self.assertIn(spec.stereotype, UML.recipes.get_stereotypes(subject))
                self.assertEqual(spec.attribute.type.name, "String")
                self.assertIs(spec.stereotype.package, spec.profile)
                self.assertEqual(read_description(subject), f"Descripción de {cls.__name__}")
        self.assertEqual(len(list(self.model.select(UML.Profile))), 1)

    def test_native_save_load_and_access_via_stereotype(self):
        description = "Texto amplio\nCon ñ, tildes y <símbolos> & más."
        save_documentation(self.component, description, "Nota aparte", self.events)
        xml = io.StringIO()
        save(xml, self.model)
        # Only native Gaphor model classes are needed to load or edit this value.
        other = ElementFactory()
        load(io.StringIO(xml.getvalue()), other, ModelingLanguageService())
        loaded = other.lookup(self.component.id)
        slot = loaded.appliedStereotype[0].slot[0]
        self.assertEqual(slot.definingFeature.name, "descripcion")
        self.assertEqual(UML.recipes.get_slot_value(slot), description)
        self.assertEqual(loaded.note, "Nota aparte")
        UML.recipes.set_slot_value(slot, "Modificado con Gaphor estándar")
        xml2 = io.StringIO()
        save(xml2, other)
        third = ElementFactory()
        load(io.StringIO(xml2.getvalue()), third, ModelingLanguageService())
        self.assertEqual(read_description(third.lookup(self.component.id)), "Modificado con Gaphor estándar")

    def test_existing_profile_and_stereotype_reused(self):
        with Transaction(self.events):
            profile = self.model.create(UML.Profile)
            profile.name = "DocumentacionArquitectura"
            stereotype = self.model.create(UML.Stereotype)
            stereotype.name = "Describible"
            stereotype.package = profile
        save_documentation(self.component, "Nueva descripción", self.component.note, self.events)
        self.assertIs(definition(self.model).profile, profile)
        self.assertIs(definition(self.model).stereotype, stereotype)

    def test_conflicting_profile_fails_without_overwrite(self):
        save_documentation(self.component, "Original", self.component.note, self.events)
        with Transaction(self.events):
            duplicate = self.model.create(UML.Profile)
            duplicate.name = "DocumentacionArquitectura"
        with self.assertRaises(DocumentationError):
            save_documentation(self.component, "No guardar", "No guardar", self.events)
        self.assertEqual(self.component.note, "Nota original áéíóú")

    def test_invalid_existing_type_rolls_back_new_schema_and_note(self):
        with Transaction(self.events):
            profile = self.model.create(UML.Profile)
            profile.name = "DocumentacionArquitectura"
            stereotype = self.model.create(UML.Stereotype)
            stereotype.name = "Describible"
            stereotype.package = profile
            attribute = self.model.create(UML.Property)
            attribute.name = "descripcion"
            stereotype.ownedAttribute = attribute
            wrong_type = self.model.create(UML.PrimitiveType)
            wrong_type.name = "Integer"
            attribute.type = wrong_type
        before = {e.id for e in self.model}
        with self.assertRaises(DocumentationError):
            save_documentation(self.component, "No guardar", "No guardar", self.events)
        self.assertEqual({e.id for e in self.model}, before)
        self.assertEqual(self.component.note, "Nota original áéíóú")

    def test_two_models_keep_values_and_schema_separate(self):
        other_events = EventManager()
        other = ElementFactory(other_events)
        other_component = other.create(UML.Component)
        save_documentation(self.component, "Proyecto A", "Nota A", self.events)
        save_documentation(other_component, "Proyecto B", "Nota B", other_events)
        self.assertEqual(read_description(self.component), "Proyecto A")
        self.assertEqual(read_description(other_component), "Proyecto B")
        self.assertIsNot(definition(self.model).profile, definition(other).profile)
        self.assertEqual(self.component.note, "Nota A")
        self.assertEqual(other_component.note, "Nota B")

    def test_write_portability_fixture(self):
        output = os.environ.get("GAPHOR_DESCRIPTION_TEST_OUTPUT")
        if not output:
            self.skipTest("El runner proporciona la carpeta temporal")
        save_properties(self.component, "Descripción portátil\nLínea 2: ñ & <texto>", "Nota independiente", "color: red;", self.events)
        with Transaction(self.events):
            diagram = self.model.create(UML.Diagram)
            diagram.name = "Prueba temporal del editor"
            diagram.diagramType = "uml"
            item = diagram.create(ComponentItem, subject=self.component)
            item.matrix.translate(100, 100)
            item.width = 300
            item.height = 180
        with (Path(output) / "portable.gaphor").open("w", encoding="utf-8") as stream:
            save(stream, self.model)

    def test_stale_editor_does_not_overwrite_newer_content(self):
        window = self.window()
        save_documentation(self.component, "Cambio externo", self.component.note, self.events)
        window.description_buffer.set_text("Cambio antiguo")
        self.assertFalse(window.save())
        self.assertEqual(read_description(self.component), "Cambio externo")
        self.assertTrue(window.error.get_visible())

    def test_deleted_target_does_not_save(self):
        window = self.window()
        with Transaction(self.events):
            self.component.unlink()
        window.description_buffer.set_text("No guardar")
        self.assertFalse(window.save())
        self.assertEqual(len(list(self.model.select(UML.Profile))), 0)

    def test_double_click_routes_by_session_and_f2_delegates(self):
        original = textedit.instant_editor
        first = self.service()
        second_events = EventManager()
        second = self.service(second_events, ElementFactory(second_events))
        first.open_element = Mock()
        second.open_element = Mock()
        item = SimpleNamespace(subject=None)
        # Use an actual Presentation for target resolution.
        with Transaction(self.events):
            diagram = self.model.create(UML.Diagram)
            item = diagram.create(ComponentItem, subject=self.component)
        self.assertTrue(textedit.instant_editor(item, None, self.events, (1, 1)))
        first.open_element.assert_called_once_with(item)
        second.open_element.assert_not_called()
        with patch.object(plugin, "_original_instant_editor", return_value=True) as native:
            self.assertTrue(textedit.instant_editor(item, None, self.events))
            native.assert_called_once_with(item, None, self.events, None)
        first.shutdown()
        self.services.remove(first)
        self.assertIs(textedit.instant_editor, plugin._route_instant_editor)
        second.shutdown()
        self.services.remove(second)
        self.assertIs(textedit.instant_editor, original)

    def test_native_double_click_diagram_still_opens_diagram(self):
        service = self.service()
        service.open_element = Mock()
        with Transaction(self.events):
            diagram = self.model.create(UML.Diagram)
        recorder = Mock()
        gesture = Mock()
        gesture.get_widget.return_value.selection.hovered_item = SimpleNamespace(subject=diagram)
        textedit.on_double_click(gesture, 2, 1, 1, recorder)
        self.assertIsInstance(recorder.handle.call_args.args[0], DiagramOpened)
        self.assertIs(recorder.handle.call_args.args[0].diagram, diagram)
        service.open_element.assert_not_called()

    def test_menu_tracks_tree_and_diagram_selections(self):
        service = self.service()
        service.open_element = Mock()
        self.events.handle(ModelSelectionChanged(None, self.component))
        service.edit_description()
        service.open_element.assert_called_with(self.component)
        self.events.handle(DiagramSelectionChanged(None, None, set()))
        service.edit_description()
        service.open_element.assert_called_with(None)

    def test_preview_refreshes_after_save_and_undo(self):
        self.service()
        page = plugin.DescriptionPropertyPage(self.component, self.events)
        self.assertIsNotNone(page.construct())
        self.assertEqual(page.preview.get_text(), "Sin descripción")
        save_documentation(self.component, "Vista actualizada", self.component.note, self.events)
        drain_events()
        self.assertEqual(page.preview.get_text(), "Vista actualizada")
        self.undo.undo_transaction()
        drain_events()
        self.assertEqual(page.preview.get_text(), "Sin descripción")
        page.close()

    def test_escape_cancels_and_window_is_resizable(self):
        window = self.window()
        self.assertTrue(window.get_modal())
        self.assertTrue(window.get_resizable())
        self.assertEqual(window.get_default_size(), (900, 650))
        self.assertIsNotNone(window.paned.get_start_child())
        self.assertIsNotNone(window.paned.get_end_child())
        self.assertTrue(window.paned.get_wide_handle())
        window.paned.set_position(200)
        self.assertEqual(window.paned.get_position(), 200)
        window.description_buffer.set_text("Cancelar con Escape")
        self.assertTrue(window._key_pressed(None, Gdk.KEY_Escape, 0, 0))
        self.assertEqual(read_description(self.component), "")

    def test_unsupported_version_does_not_patch_native_editor(self):
        original = textedit.instant_editor
        with patch.object(plugin, "version", return_value="9.0.0"):
            service = self.service()
        self.assertFalse(service.compatible)
        self.assertIs(textedit.instant_editor, original)


if __name__ == "__main__":
    unittest.main()
