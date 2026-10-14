import io
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

from gi.repository import Gdk, Gtk
from gaphor import UML
from gaphor.core import Transaction, event_handler
from gaphor.core.modeling import ElementFactory
from gaphor.diagram.event import DiagramOpened
from gaphor.storage.load import load
from gaphor.storage.save import save

import gaphor_description_editor as plugin
from gaphor_description_editor.model import read_css, read_description, save_properties
import test_plugin as base


class DiagramTests(unittest.TestCase):
    setUp = base.PluginTests.setUp
    tearDown = base.PluginTests.tearDown
    window = base.PluginTests.window
    service = base.PluginTests.service

    def diagram(self, name="Flujo", owner=None, cls=UML.ActivityDiagram):
        with Transaction(self.events):
            diagram = self.model.create(cls)
            diagram.name = name
            diagram.element = owner or self.component
        return diagram

    def rows(self, window):
        result = []
        index = 0
        while row := window.diagrams_page.listbox.get_row_at_index(index):
            result.append(row)
            index += 1
        return result

    def record_open(self, window):
        opened = []

        @event_handler(DiagramOpened)
        def record(event):
            self.assertTrue(window.finished, "Properties must close before opening the diagram")
            opened.append(event.diagram)

        self.events.subscribe(record)
        return opened

    def test_three_tabs_empty_list_and_no_model_changes(self):
        before = self.model.size()
        window = self.window()
        self.assertEqual([window.tabs.get_tab_label_text(window.tabs.get_nth_page(i)) for i in range(3)],
                         ["Documentación", "Diagramas", "Estilo CSS"])
        self.assertEqual(self.rows(window), [])
        self.assertEqual(window.diagrams_page.empty.get_text(), "Este elemento no tiene diagramas hijos")
        self.assertFalse(window.diagrams_page.open_button.get_sensitive())
        window.diagrams_page.open_selected()
        self.assertFalse(window.finished)
        self.assertEqual(self.model.size(), before)

    def test_only_direct_children_sorted_and_same_names_distinguished(self):
        last = self.diagram("Zulu")
        first = self.diagram("alfa")
        duplicate = self.diagram("alfa", cls=UML.ComponentDiagram)
        self.diagram("Nieto oculto", owner=first)
        window = self.window()
        rows = self.rows(window)
        self.assertEqual({row.diagram for row in rows}, {first, duplicate, last})
        self.assertIs(rows[-1].diagram, last)
        labels = [row.get_child().get_first_child().get_text() for row in rows[:2]]
        self.assertNotEqual(*labels)
        self.assertTrue(all(label.startswith("alfa · ") for label in labels))
        self.assertEqual(rows[0].get_child().get_last_child().get_text(), "Activity Diagram")

    def test_package_component_artifact_and_long_unicode_names(self):
        for cls in (UML.Package, UML.Component, UML.Artifact):
            with self.subTest(kind=cls.__name__), Transaction(self.events):
                subject = self.model.create(cls)
                diagram = self.diagram("Descripción ñ " * 60, owner=subject)
                window = plugin.DocumentationWindow(None, subject, self.events, Mock())
                self.windows.append(window)
                self.assertEqual([row.diagram for row in self.rows(window)], [diagram])
                label = self.rows(window)[0].get_child().get_first_child()
                self.assertIn(diagram.name, label.get_tooltip_text())

    def test_list_refreshes_on_tab_entry_after_create_rename_and_move(self):
        existing = self.diagram("Zulu")
        window = self.window()
        added = self.diagram("Alfa")
        window.tabs.set_current_page(window.tabs.page_num(window.diagrams_page))
        self.assertEqual([row.diagram for row in self.rows(window)], [added, existing])
        window.tabs.set_current_page(0)
        with Transaction(self.events):
            existing.name = "Antes"
            added.element = existing
        window.tabs.set_current_page(window.tabs.page_num(window.diagrams_page))
        self.assertEqual([row.diagram for row in self.rows(window)], [existing])
        self.assertEqual(self.rows(window)[0].get_child().get_first_child().get_text(), "Antes")

    def test_double_click_enter_and_button_use_same_close_then_open_flow(self):
        diagram = self.diagram()
        for action in ("double-click", "enter", "button"):
            with self.subTest(action=action):
                window = self.window()
                opened = self.record_open(window)
                page = window.diagrams_page
                row = self.rows(window)[0]
                page.listbox.select_row(row)
                self.assertTrue(page.open_button.get_sensitive())
                if action == "double-click":
                    page.listbox.emit("row-activated", row)
                elif action == "enter":
                    self.assertTrue(page.keys.emit("key-pressed", Gdk.KEY_Return, 0, Gdk.ModifierType(0)))
                else:
                    page.open_button.emit("clicked")
                self.assertEqual(opened, [diagram])
                self.assertIsNone(window.confirmation)
                self.assertFalse(window.open_child_diagram(diagram))
                self.assertEqual(opened, [diagram])

    def test_each_documentation_field_and_css_trigger_confirmation(self):
        diagram = self.diagram()
        for field in ("description_buffer", "note_buffer", "css_buffer"):
            with self.subTest(field=field):
                window = self.window()
                getattr(window, field).set_text("color: navy;")
                self.assertFalse(window.open_child_diagram(diagram))
                self.assertIsNotNone(window.confirmation)
                original = window.confirmation
                window.open_child_diagram(diagram)
                self.assertIs(window.confirmation, original)
                window.confirmation.response(Gtk.ResponseType.CANCEL)
                self.assertFalse(window.finished)
                window.cancel()

    def test_save_then_open_is_atomic_and_undoable(self):
        diagram = self.diagram()
        self.undo.clear_undo_stack()
        window = self.window()
        opened = self.record_open(window)
        window.description_buffer.set_text("Responsabilidad")
        window.note_buffer.set_text("Nota distinta")
        window.css_buffer.set_text("color: navy;")
        window.open_child_diagram(diagram)
        window.confirmation.response(Gtk.ResponseType.ACCEPT)
        self.assertEqual(opened, [diagram])
        self.assertEqual((read_description(self.component), self.component.note, read_css(self.component)),
                         ("Responsabilidad", "Nota distinta", "color: navy;"))
        self.undo.undo_transaction()
        self.assertEqual((read_description(self.component), self.component.note, read_css(self.component)),
                         ("", "Nota original áéíóú", ""))
        self.assertIs(self.model.lookup(diagram.id), diagram)
        self.undo.redo_transaction()
        self.assertEqual(read_css(self.component), "color: navy;")

    def test_discard_opens_even_with_invalid_css_without_saving(self):
        diagram = self.diagram()
        window = self.window()
        opened = self.record_open(window)
        before = self.model.size()
        window.description_buffer.set_text("No guardar")
        window.note_buffer.set_text("No guardar")
        window.css_buffer.set_text("CSS inválido")
        window.open_child_diagram(diagram)
        window.confirmation.response(Gtk.ResponseType.REJECT)
        self.assertEqual(opened, [diagram])
        self.assertEqual(self.model.size(), before)
        self.assertEqual((read_description(self.component), self.component.note, read_css(self.component)),
                         ("", "Nota original áéíóú", ""))

    def test_cancel_escape_and_confirmation_close_keep_all_edits(self):
        diagram = self.diagram()
        window = self.window()
        opened = self.record_open(window)
        window.description_buffer.set_text("Pendiente")
        for action in ("cancel", "escape", "close"):
            window.open_child_diagram(diagram)
            dialog = window.confirmation
            if action == "cancel":
                dialog.response(Gtk.ResponseType.CANCEL)
            elif action == "escape":
                window._confirmation_key_pressed(None, Gdk.KEY_Escape, 0, 0)
            else:
                dialog.emit("close-request")
            self.assertIsNone(window.confirmation)
            self.assertFalse(window.finished)
            self.assertEqual(plugin._buffer_text(window.description_buffer), "Pendiente")
            self.assertEqual(opened, [])

    def test_invalid_css_on_navigation_preserves_all_fields_and_selects_css(self):
        diagram = self.diagram()
        window = self.window()
        opened = self.record_open(window)
        window.description_buffer.set_text("No guardar parcialmente")
        window.note_buffer.set_text("No guardar parcialmente")
        window.css_buffer.set_text("color: invalid;")
        window.open_child_diagram(diagram)
        window.confirmation.response(Gtk.ResponseType.ACCEPT)
        self.assertFalse(window.finished)
        self.assertEqual(window.tabs.get_current_page(), window.tabs.page_num(window.css_page))
        self.assertTrue(window.error.get_visible())
        self.assertEqual(read_description(self.component), "")
        self.assertEqual(self.component.note, "Nota original áéíóú")
        self.assertEqual(plugin._buffer_text(window.css_buffer), "color: invalid;")
        self.assertEqual(opened, [])

    def test_external_documentation_conflict_blocks_save_and_navigation(self):
        diagram = self.diagram()
        window = self.window()
        opened = self.record_open(window)
        window.description_buffer.set_text("Mi cambio")
        window.open_child_diagram(diagram)
        save_properties(self.component, "Cambio externo", "Otra nota", "", self.events)
        window.confirmation.response(Gtk.ResponseType.ACCEPT)
        self.assertFalse(window.finished)
        self.assertEqual(opened, [])
        self.assertEqual(read_description(self.component), "Cambio externo")
        self.assertEqual(plugin._buffer_text(window.description_buffer), "Mi cambio")

    def test_deleted_moved_and_foreign_targets_are_rejected_before_navigation(self):
        for action in ("delete", "move", "foreign"):
            with self.subTest(action=action):
                diagram = self.diagram()
                window = self.window()
                opened = self.record_open(window)
                window.note_buffer.set_text("Conservar")
                with Transaction(self.events):
                    if action == "delete":
                        diagram.unlink()
                    elif action == "move":
                        diagram.element = self.model.create(UML.Package)
                    else:
                        other = ElementFactory()
                        diagram = other.create(UML.ActivityDiagram)
                self.assertFalse(window.open_child_diagram(diagram))
                self.assertFalse(window.finished)
                self.assertIsNone(window.confirmation)
                self.assertEqual(plugin._buffer_text(window.note_buffer), "Conservar")
                self.assertEqual(opened, [])
                window.cancel()

    def test_target_moved_while_confirmation_open_does_not_save_or_close(self):
        diagram = self.diagram()
        window = self.window()
        opened = self.record_open(window)
        window.description_buffer.set_text("Pendiente")
        window.open_child_diagram(diagram)
        with Transaction(self.events):
            diagram.element = self.model.create(UML.Package)
        window.confirmation.response(Gtk.ResponseType.ACCEPT)
        self.assertFalse(window.finished)
        self.assertEqual(read_description(self.component), "")
        self.assertTrue(window.error.get_visible())
        self.assertEqual(opened, [])

    def test_parent_deleted_and_service_shutdown_invalidate_pending_navigation(self):
        diagram = self.diagram()
        service = self.service()
        service.open_element(self.component)
        window = service.editor
        opened = self.record_open(window)
        window.description_buffer.set_text("Pendiente")
        window.open_child_diagram(diagram)
        dialog = window.confirmation
        service.shutdown()
        self.services.remove(service)
        self.assertTrue(window.finished)
        self.assertIsNone(window.confirmation)
        window._navigation_response(dialog, Gtk.ResponseType.REJECT, diagram)
        self.assertEqual(opened, [])
        window = self.window()
        with Transaction(self.events):
            self.component.unlink()
        self.assertFalse(window.open_child_diagram(diagram))
        self.assertFalse(window.finished)

    def test_native_ownership_survives_save_reopen_without_extra_data(self):
        diagram = self.diagram()
        before = self.model.size()
        self.window().diagrams_page.refresh()
        stream = io.StringIO()
        save(stream, self.model)
        other = ElementFactory()
        load(io.StringIO(stream.getvalue()), other, self.language)
        self.assertIs(other.lookup(diagram.id).element, other.lookup(self.component.id))
        self.assertEqual(self.model.size(), before)
        self.assertEqual(list(self.model.select(UML.Profile)), [])

    def test_native_tabs_reused_and_two_projects_stay_isolated_with_importer(self):
        from gaphor.application import Session
        from gaphor.entrypoint import load_entry_points
        from navigation_integration import verify_navigation
        importer_source = Path(__file__).resolve().parents[2] / "gaphor-folder-diagram"
        sys.path.insert(0, str(importer_source))
        from gaphor_folder_diagram import FolderDiagramService
        sessions = []
        try:
            services = dict(load_entry_points("gaphor.services"))
            services.update(description_editor=plugin.DescriptionEditor, folder_diagram=FolderDiagramService)
            for _ in range(2):
                sessions.append(Session(services=services))
            verify_navigation(sessions)
        finally:
            for session in sessions:
                session.shutdown()
            sys.path.remove(str(importer_source))
