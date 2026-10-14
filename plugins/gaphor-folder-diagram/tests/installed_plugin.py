"""Integration with both installed plugins, menus and independent sessions."""

import contextlib
from importlib.metadata import distributions
import logging
import os
from pathlib import Path
import tempfile
import traceback
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

output = Path(os.environ["GAPHOR_FOLDER_TEST_OUTPUT"])


def menu_entries(menu):
    for index in range(menu.get_n_items()):
        label = menu.get_item_attribute_value(index, "label", None)
        action = menu.get_item_attribute_value(index, "action", None)
        if label:
            yield label.get_string(), action.get_string() if action else None
        for link in ("section", "submenu"):
            if child := menu.get_item_link(index, link):
                yield from menu_entries(child)


with (output / "installed-plugin.txt").open("w", encoding="utf-8") as report:
    try:
        with contextlib.redirect_stdout(report), contextlib.redirect_stderr(report):
            logging.basicConfig(stream=report, level=logging.WARNING, force=True)
            from gi.repository import Gtk, GLib
            from gaphor import UML
            from gaphor.application import Session
            from gaphor.core import Transaction
            from gaphor.ui.actiongroup import window_action_group
            from gaphor.ui.event import ModelSelectionChanged
            from gaphor_description_editor.model import read_description, save_documentation
            from gaphor_folder_diagram.model import create_capture, validate_layout
            from gaphor_folder_diagram.scanner import scan_folder
            from zoom_integration import assert_style_isolation, exercise_zoom

            Gtk.init()
            # Gaphor's plugin finder can return an unrelated distribution for a
            # named lookup. Filter actual metadata, also detecting old duplicates.
            installed = list(distributions())
            for name, expected in (("gaphor-folder-diagram", "0.1.1"),
                                   ("gaphor-description-editor", "0.3.0")):
                matches = [d for d in installed if d.metadata["Name"] == name]
                assert len(matches) == 1, (name, [d.version for d in matches])
                assert matches[0].version == expected
            services = [ep for d in installed for ep in d.entry_points
                        if ep.group == "gaphor.services" and ep.name == "folder_diagram"]
            assert len(services) == 1
            sessions = [Session(), Session()]
            try:
                with tempfile.TemporaryDirectory(prefix="gaphor-folder-integration-") as directory:
                    (Path(directory) / "archivo.ts").write_text("", encoding="utf-8")
                    snapshot = scan_folder(directory)
                    captures = []
                    styles = []
                    for index, session in enumerate(sessions):
                        session.get_service("main_window").window = Gtk.Window()
                        importer = session.get_service("folder_diagram")
                        editor = session.get_service("description_editor")
                        assert importer.compatible and editor.compatible
                        entries = list(menu_entries(session.get_service("tools_menu").menu))
                        assert sum(label == "Custom tools" for label, _ in entries) == 1
                        assert ("Importar/leer componente en crudo…", "win.import-raw-component") in entries
                        assert ("Propiedades…", "win.edit-description") in entries
                        model = session.get_service("element_factory")
                        events = session.get_service("event_manager")
                        with Transaction(events):
                            destination = model.create(UML.Package)
                            destination.name = f"Proyecto {index}"
                        events.handle(ModelSelectionChanged(None, destination))
                        group = window_action_group(session.component_registry)
                        group.activate_action("import-raw-component", None)
                        assert importer.window.destinations[importer.window.destination.get_selected()] is destination
                        importer.window.cancel()
                        capture = create_capture(model, events, snapshot, destination)
                        artifact = next(model.select(UML.Artifact))
                        save_documentation(artifact, f"Descripción {index}", f"Nota {index}", events)
                        assert read_description(artifact) == f"Descripción {index}"
                        assert artifact.note == f"Nota {index}"
                        validate_layout(capture.diagram)
                        captures.append(capture)
                        styles.append(exercise_zoom(session, capture, ("color: navy;", "color: maroon;")[index]))
                    assert captures[0].package.model is not captures[1].package.model
                    assert captures[0].package.name == captures[1].package.name
                    assert_style_isolation(*styles)
            finally:
                for session in sessions:
                    session.shutdown()
            report.write("PASS: 0.1.1 sin servicios duplicados; menú, destino, Ctrl+rueda nativo, refresco CSS y dos proyectos con Propiedades.\n")
            (output / "installed-plugin-status.txt").write_text("PASS", encoding="utf-8")
    except Exception:
        traceback.print_exc(file=report)
        (output / "installed-plugin-status.txt").write_text("FAIL", encoding="utf-8")
