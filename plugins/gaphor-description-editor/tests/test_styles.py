import io
import os
from pathlib import Path
from unittest.mock import Mock
import unittest

from gaphor import UML
from gaphor.core import Transaction
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import ElementFactory, StyleSheet
from gaphor.core.modeling.diagram import StyledItem
from gaphor.core.styling import PrefersColorScheme
from gaphor.diagram.export import save_png
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.storage.load import load
from gaphor.storage.save import save
from gaphor.UML.classes.component import ComponentItem
from gaphor.UML.classes.package import PackageItem
from gaphor.UML.deployments.artifact import ArtifactItem
from gaphor.UML.classes.dependency import DependencyItem

import test_plugin as base
import gaphor_description_editor as plugin
from gaphor_description_editor.model import (
    DocumentationError, definition, read_css, read_description, save_documentation, save_properties,
)
from gaphor_description_editor.styles import CssError, parse_css


class StyleTests(unittest.TestCase):
    setUp = base.PluginTests.setUp
    tearDown = base.PluginTests.tearDown
    service = base.PluginTests.service
    window = base.PluginTests.window

    def diagram(self):
        with Transaction(self.events):
            diagram = self.model.create(UML.ComponentDiagram)
            diagram.name = "Propiedades CSS"
        return diagram

    def item(self, diagram, cls=UML.Component, item_cls=ComponentItem, parent=None, subject=None):
        with Transaction(self.events):
            subject = subject or self.model.create(cls)
            subject.name = subject.name or "Mismo nombre"
            return diagram.create(item_cls, subject=subject, parent=parent)

    def set_css(self, subject, css):
        return save_properties(subject, read_description(subject), subject.note or "", css, self.events)

    def sheet(self, css="diagram { color: black; font-size: 14; background-color: white; }"):
        with Transaction(self.events):
            sheet = self.model.style_sheet or self.model.create(StyleSheet)
            sheet.styleSheet = css
        return sheet

    def style(self, item, sheet=None, mode=PrefersColorScheme.NONE):
        return (sheet or self.model.style_sheet or StyleSheet()).compute_style(StyledItem(item), mode)

    def test_parser_accepts_native_visual_values_and_preserves_cache(self):
        parsed = parse_css('/* ejemplo */ background-color: lightblue; color: rgba(1, 2, 3, 0.5); '
                           'font-family: "DejaVu Sans"; font-size: 14px; font-weight: normal; '
                           'padding: 8 12; dash-style: 7 5; opacity: 0.5;')
        self.assertEqual(parsed["font-size"], 14)
        self.assertEqual(parsed["padding"], (8, 12, 8, 12))
        parsed["font-size"] = 500
        self.assertEqual(parse_css("font-size: 14;")["font-size"], 14)
        self.assertEqual(parse_css(" /* sin personalización */ "), {})

    def test_parser_rejects_unsupported_or_unsafe_values_with_location(self):
        for css in (
            "component { color: red; }", "@import 'other.css';", "--custom: blue;", "color: var(--a);",
            "line-style: sloppy;", "content: 'text';", "color: definitely-not-a-color;",
            "font-size: -3;", "opacity: 2;", "padding: -1;", "padding: 1 2 3 4 5;",
            "dash-style: -2 4;", "dash-style: 0 0;", "font-size: 1e999;", "font-size: 2em;",
            "color: red !important;", "color: red;\nfont-size: ;", "font-family: url(http://example.com);",
            "dash-style: ;", "font-family: Arial color: red;",
        ):
            with self.subTest(css=css), self.assertRaisesRegex(CssError, "línea .*columna"):
                parse_css(css)

    def test_three_fields_are_one_undo_and_redo(self):
        window = self.window()
        window.description_buffer.set_text("Descripción nueva")
        window.note_buffer.set_text("Nota nueva")
        window.css_buffer.set_text("color: navy;")
        self.assertTrue(window.save())
        self.assertEqual((read_description(self.component), self.component.note, read_css(self.component)),
                         ("Descripción nueva", "Nota nueva", "color: navy;"))
        self.undo.undo_transaction()
        self.assertEqual((read_description(self.component), self.component.note, read_css(self.component)),
                         ("", "Nota original áéíóú", ""))
        self.undo.redo_transaction()
        self.assertEqual(read_css(self.component), "color: navy;")
        self.assertEqual(len(list(self.model.select(UML.Profile))), 1)

    def test_invalid_css_saves_nothing_and_keeps_editor_open(self):
        window = self.window()
        before = self.model.size()
        window.description_buffer.set_text("No guardar")
        window.note_buffer.set_text("No guardar")
        window.css_buffer.set_text("color: wrong;")
        self.assertFalse(window.save())
        self.assertFalse(window.finished)
        self.assertEqual(window.tabs.get_current_page(), 1)
        self.assertEqual(self.model.size(), before)
        self.assertEqual(self.component.note, "Nota original áéíóú")

    def test_cancel_css_is_not_previewed_and_tabs_are_editable(self):
        self.service()
        item = self.item(self.diagram(), subject=self.component)
        before = self.style(item)["color"]
        window = self.window()
        self.assertTrue(window.get_title().startswith("Propiedades —"))
        self.assertEqual(window.tabs.get_n_pages(), 2)
        self.assertTrue(window.css_view.get_monospace())
        window.css_buffer.set_text("color: red;")
        self.assertEqual(self.style(item)["color"], before)
        window.cancel()
        self.assertEqual(read_css(self.component), "")

    def test_old_models_lazy_schema_and_legacy_api_preserve_css(self):
        save_documentation(self.component, "Anterior", self.component.note, self.events)
        old_attribute = definition(self.model).attribute
        self.assertIsNone(definition(self.model, "css").attribute)
        self.set_css(self.component, "color: red;")
        self.assertIs(definition(self.model).attribute, old_attribute)
        self.assertEqual(definition(self.model, "css").attribute.type.name, "String")
        ids = {element.id for element in self.model}
        save_documentation(self.component, "Actualizada", "Nueva nota", self.events)
        self.assertEqual(read_css(self.component), "color: red;")
        for css in ("color: navy;", "", "color: green;"):
            self.set_css(self.component, css)
            self.assertEqual({element.id for element in self.model}, ids)

    def test_css_schema_conflict_rolls_back_all_fields(self):
        self.set_css(self.component, "color: red;")
        with Transaction(self.events):
            wrong = self.model.create(UML.PrimitiveType)
            wrong.name = "Integer"
            definition(self.model, "css").attribute.type = wrong
        before = {element.id for element in self.model}
        with self.assertRaises(DocumentationError):
            save_properties(self.component, "No guardar", "No guardar", "color: blue;", self.events)
        self.assertEqual({element.id for element in self.model}, before)
        self.assertEqual(read_description(self.component), "")
        self.assertEqual(self.component.note, "Nota original áéíóú")

    def test_changed_css_is_detected_by_stale_editor(self):
        window = self.window()
        self.set_css(self.component, "color: red;")
        window.css_buffer.set_text("color: blue;")
        self.assertFalse(window.save())
        self.assertEqual(read_css(self.component), "color: red;")

    def test_all_appearances_future_appearances_and_homonyms(self):
        self.service()
        first = self.item(self.diagram(), subject=self.component)
        second = self.item(self.diagram(), subject=self.component)
        unrelated = self.item(first.diagram)
        with Transaction(self.events):
            unrelated.subject.name = self.component.name
        self.set_css(self.component, "background-color: lightblue; color: navy;")
        third = self.item(self.diagram(), subject=self.component)
        for item in (first, second, third):
            self.assertEqual(self.style(item)["color"], (0, 0, 128 / 255, 1))
            self.assertEqual(self.style(item)["background-color"], parse_css("background-color: lightblue;")["background-color"])
        self.assertNotEqual(self.style(unrelated)["color"], self.style(first)["color"])

    def test_nested_figures_keep_native_style_and_own_css(self):
        self.service()
        sheet = self.sheet()
        diagram = self.diagram()
        parent = self.item(diagram, UML.Package, PackageItem)
        child = self.item(diagram, parent=parent)
        grandchild = self.item(diagram, UML.Artifact, ArtifactItem, parent=child)
        baseline_child = self.style(child)
        baseline_grandchild = self.style(grandchild)
        self.set_css(parent.subject, "color: red; font-size: 24; line-width: 5; font-weight: normal;")
        for key in ("color", "font-size", "line-width"):
            self.assertEqual(self.style(child)[key], baseline_child[key])
            self.assertEqual(self.style(grandchild)[key], baseline_grandchild[key])
        self.set_css(child.subject, "color: blue; font-size: 18;")
        self.assertEqual(self.style(child)["color"], (0, 0, 1, 1))
        self.assertEqual(self.style(grandchild)["color"], baseline_grandchild["color"])
        self.set_css(parent.subject, "color: green; font-size: 30;")
        self.assertEqual(self.style(child)["font-size"], 18)
        self.assertEqual(self.style(grandchild)["font-size"], baseline_grandchild["font-size"])
        self.assertEqual(sheet.styleSheet, "diagram { color: black; font-size: 14; background-color: white; }")

    def test_own_labels_receive_custom_typography(self):
        self.service()
        self.sheet()
        parent = self.item(self.diagram(), UML.Package, PackageItem)
        self.set_css(parent.subject, "color: navy; font-size: 22; font-weight: normal;")
        style = self.style(parent)
        name = next(node for node in parent.css_nodes() if node.name == "name")
        label_style = style["-gaphor-compiled-style-sheet"].compute_style(name.style_node(StyledItem(parent)))
        for key in ("color", "font-size", "font-weight"):
            self.assertEqual(label_style[key], style[key])

    def test_native_cascade_opacity_and_relative_sizes_are_not_applied_twice(self):
        self.sheet("diagram { color: black; font-size: 14; } component { opacity: 0.5; font-size: large; }")
        item = self.item(self.diagram())
        native = self.style(item)
        self.service()
        self.assertEqual(self.style(item)["color"], native["color"])
        self.assertEqual(self.style(item)["font-size"], native["font-size"])
        self.set_css(item.subject, "color: red; font-size: large;")
        self.assertEqual(self.style(item)["color"], (1, 0, 0, 0.5))
        self.assertEqual(self.style(item)["font-size"], 14 * 1.2)

    def test_clear_undo_redo_and_native_slot_edits_refresh(self):
        self.service()
        self.sheet()
        item = self.item(self.diagram(), subject=self.component)
        self.undo.clear_undo_stack()
        self.set_css(self.component, "color: red;")
        self.assertEqual(self.style(item)["color"], (1, 0, 0, 1))
        self.undo.undo_transaction()
        self.assertEqual(self.style(item)["color"], (0, 0, 0, 1))
        self.undo.redo_transaction()
        self.assertEqual(self.style(item)["color"], (1, 0, 0, 1))
        slot = next(slot for slot in self.component.appliedStereotype[0].slot if slot.definingFeature.name == "css")
        updates = []
        item.diagram.register_view(Mock(request_update=lambda *args: updates.append(args)))
        with Transaction(self.events):
            UML.recipes.set_slot_value(slot, "color: blue;")
        base.drain_events()
        self.assertTrue(updates)
        self.assertEqual(self.style(item)["color"], (0, 0, 1, 1))
        self.set_css(self.component, "")
        self.assertEqual(self.style(item)["color"], (0, 0, 0, 1))

    def test_invalid_native_css_falls_back_without_losing_text(self):
        self.service()
        self.sheet()
        item = self.item(self.diagram(), subject=self.component)
        self.set_css(self.component, "color: red;")
        self.style(item)  # Populate cache before the native edit.
        slot = next(slot for slot in self.component.appliedStereotype[0].slot if slot.definingFeature.name == "css")
        with Transaction(self.events):
            UML.recipes.set_slot_value(slot, "color: invalid-color;")
        self.assertEqual(self.style(item)["color"], (0, 0, 0, 1))
        self.assertEqual(read_css(self.component), "color: invalid-color;")

    def test_light_dark_native_styles_and_global_edits_remain_active(self):
        sheet = self.sheet("diagram { color: black; } @media dark-mode { diagram { color: white; } }")
        self.service()
        parent = self.item(self.diagram(), UML.Package, PackageItem)
        child = self.item(parent.diagram, parent=parent)
        self.set_css(parent.subject, "color: red;")
        for mode, expected in ((PrefersColorScheme.LIGHT, (0, 0, 0, 1)), (PrefersColorScheme.DARK, (1, 1, 1, 1))):
            self.assertEqual(self.style(parent, sheet, mode)["color"], (1, 0, 0, 1))
            self.assertEqual(self.style(child, sheet, mode)["color"], expected)
        with Transaction(self.events):
            # A component rule overrides the native component-diagram defaults.
            sheet.styleSheet = "component { color: navy; }"
        self.assertIs(self.model.style_sheet, sheet)
        for mode in (PrefersColorScheme.LIGHT, PrefersColorScheme.DARK):
            self.assertEqual(self.style(child, sheet, mode)["color"], (0, 0, 128 / 255, 1))
            self.assertEqual(self.style(parent, sheet, mode)["color"], (1, 0, 0, 1))

    def test_supported_shapes_include_relationships(self):
        self.service()
        for cls, item_cls in ((UML.Component, ComponentItem), (UML.Artifact, ArtifactItem),
                              (UML.Package, PackageItem), (UML.Dependency, DependencyItem)):
            with self.subTest(cls=cls.__name__):
                item = self.item(self.diagram(), cls, item_cls)
                self.set_css(item.subject, "color: navy; line-width: 3;")
                self.assertEqual(self.style(item)["color"], (0, 0, 128 / 255, 1))
                self.assertEqual(self.style(item)["line-width"], 3)

    def test_two_models_and_shutdown_restore_native_compute(self):
        native = StyleSheet.compute_style
        first = self.service()
        item = self.item(self.diagram(), subject=self.component)
        self.set_css(self.component, "color: red;")
        other_events = EventManager()
        other = ElementFactory(other_events)
        second = self.service(other_events, other)
        with Transaction(other_events):
            subject = other.create(UML.Component)
            diagram = other.create(UML.ComponentDiagram)
            other_item = diagram.create(ComponentItem, subject=subject)
        save_properties(subject, "", "", "color: blue;", other_events)
        self.assertEqual(self.style(item)["color"], (1, 0, 0, 1))
        self.assertEqual(self.style(other_item)["color"], (0, 0, 1, 1))
        first.shutdown()
        self.services.remove(first)
        self.assertIsNot(StyleSheet.compute_style, native)
        self.assertNotEqual(self.style(item)["color"], (1, 0, 0, 1))
        second.shutdown()
        self.services.remove(second)
        self.assertIs(StyleSheet.compute_style, native)

    def test_save_reopen_rebuilds_css_and_exports_nested_example(self):
        self.service()
        sheet = self.sheet()
        diagram = self.diagram()
        parent = self.item(diagram, UML.Package, PackageItem)
        child = self.item(diagram, UML.Artifact, ArtifactItem, parent=parent)
        with Transaction(self.events):
            parent.subject.name = "Paquete con estilo propio"
            child.subject.name = "archivo.ts — estilo independiente"
            child.subject.package = parent.subject
            parent.width, parent.height = 680, 300
            child.width, child.height = 380, 90
            parent.matrix.translate(30, 60)
            child.matrix.translate(50, 120)
        self.set_css(parent.subject, "background-color: lightblue; color: navy; font-size: 22; line-width: 3;")
        self.set_css(child.subject, "background-color: beige; color: darkgreen; font-size: 16;")
        stream = io.StringIO()
        save(stream, self.model)
        other_events = EventManager()
        other = ElementFactory(other_events)
        self.service(other_events, other)
        load(io.StringIO(stream.getvalue()), other, ModelingLanguageService())
        loaded = other.lookup(parent.id)
        self.assertEqual(self.style(loaded)["color"], self.style(parent)["color"])
        self.assertEqual(other.style_sheet.styleSheet, sheet.styleSheet)
        if output := os.environ.get("GAPHOR_DESCRIPTION_TEST_OUTPUT"):
            save_png(str(Path(output) / "nested-css.png"), diagram)
            with (Path(output) / "nested-css.gaphor").open("w", encoding="utf-8") as document:
                document.write(stream.getvalue())
