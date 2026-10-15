"""Native sessions, hit testing, GTK clipboard and coexistence; temporary models only."""

import asyncio
import contextlib
import logging
import os
from pathlib import Path
import sys
import traceback
from types import SimpleNamespace
from unittest.mock import patch

installed = globals().get("INSTALLED", False)
plugins = Path(__file__).resolve().parents[2]
if not installed:
    for directory in ("gaphor-copy-reference", "gaphor-description-editor", "gaphor-folder-diagram"):
        sys.path.insert(0, str(plugins / directory))
sys.path.insert(0, str(Path(__file__).parent))
output = Path(os.environ["GAPHOR_COPY_REFERENCE_TEST_OUTPUT"])
prefix = "installed-plugin" if installed else "integration"


async def settle():
    from gi.repository import GLib
    context = GLib.MainContext.default()
    for _ in range(3):
        while context.pending():
            context.iteration(False)
        await asyncio.sleep(0.01)


async def verify(sessions):
    from gi.repository import Gdk, Gio, GLib, Gtk
    from gaphas.tool.zoom import on_scroll
    from gaphor import UML
    from gaphor.core import Transaction
    from gaphor.diagram.event import DiagramOpened
    from gaphor.UML.classes.package import PackageItem
    from gaphor.UML.deployments.artifact import ArtifactItem
    from gaphor.ui import diagrampage, modelbrowser
    from gaphor.ui.actiongroup import window_action_group
    from gaphor_copy_reference.paths import ReferenceError
    from gaphor_description_editor.model import save_properties
    from helpers import action_target, clipboard_text, entries

    errors = []
    opened = []
    captures = []
    asyncio.get_running_loop().set_exception_handler(lambda _loop, error: errors.append(error))
    try:
        with patch("sys.excepthook", side_effect=lambda *error: errors.append(error)):
            for number, session in enumerate(sessions):
                service = session.get_service("copy_reference")
                editor = session.get_service("description_editor")
                importer = session.get_service("folder_diagram")
                assert service.compatible and editor.compatible and importer.compatible
                model = session.get_service("element_factory")
                events = session.get_service("event_manager")
                diagrams = session.get_service("diagrams")
                window = Gtk.Window()
                session.get_service("main_window").window = window
                window.set_child(diagrams.open())
                group = window_action_group(session.component_registry)
                window.insert_action_group("win", group)
                opened.append((diagrams, window))
                with Transaction(events):
                    # Identical IDs in separate projects must never cross sessions.
                    package = model.create_as(UML.Package, "same-package")
                    package.name = f"Proyecto{number}"
                    diagram = model.create_as(UML.ComponentDiagram, "same-diagram")
                    diagram.name = "Temporal"
                    root = diagram.create(PackageItem, subject=package)
                    root.width, root.height = 600, 400
                    element = model.create_as(UML.Artifact, "same-artifact")
                    element.name = "Archivo á.tsx"
                    element.package = package
                    item = diagram.create(ArtifactItem, subject=element, parent=root)
                    item.matrix.translate(60, 80)
                    item.width, item.height = 210, 70
                    previous = model.create(UML.Artifact)
                    previous.name = "Seleccion anterior.txt"
                    previous_item = diagram.create(ArtifactItem, subject=previous, parent=root)
                    previous_item.matrix.translate(310, 80)
                events.handle(DiagramOpened(diagram))
                await settle()
                view = diagrams.get_current_view()
                view.selection.focused_item = previous_item
                original = list(entries(diagrampage.popup_model(element)))
                menu = diagrampage.popup_model(element)
                def set_menu(value):
                    nonlocal menu
                    menu = value
                popup_opened = False
                def popup():
                    nonlocal popup_opened
                    # GTK can release the gesture event while opening a popover.
                    # All entries must already be present at this point.
                    assert "Copiar ruta relativa" in [e[0] for e in entries(menu)]
                    popup_opened = True
                context = SimpleNamespace(set_menu_model=set_menu, set_has_arrow=lambda value: None,
                                          set_pointing_to=lambda value: None, popup=popup)
                controller = SimpleNamespace(
                    get_widget=lambda: view,
                    get_last_event=lambda: None if popup_opened else SimpleNamespace(triggers_context_menu=lambda: True),
                    get_current_event_state=lambda: Gdk.ModifierType.CONTROL_MASK,
                )

                def right_click():
                    nonlocal popup_opened
                    popup_opened = False
                    x, y = view.get_matrix_i2v(item).transform_point(35, 35)
                    found, _ = diagrampage.default_find_item_and_handle_at_point(view, (x, y))
                    assert found is item, (found, item)
                    service.on_context_pressed(controller, 1, x, y, context, diagram)
                    assert popup_opened

                right_click()
                target = action_target(menu, "Copiar ruta relativa")
                group.activate_action("copy-reference-path", GLib.Variant.new_string(target))
                expected = f"Proyecto{number}/Archivo á.tsx"
                assert clipboard_text(window) == expected
                assert view.selection.focused_item is previous_item
                assert [(a,b) for a,b,_ in entries(menu)][:len(original)] == [(a,b) for a,b,_ in original]
                # Re-run native hit testing after Ctrl+wheel and panning.
                assert on_scroll(controller, 0, -1)
                view.matrix.translate(-40, 20)
                await settle()
                right_click()
                assert action_target(menu, "Copiar ruta relativa") == target
                assert len([e for e in entries(menu) if e[0] == "Copiar nombre"]) == 1
                save_properties(element, "Descripción temporal", "Nota", "color: navy;", events)
                await settle()
                assert service._resolve(target, True) == expected
                tree_menu = modelbrowser.popup_model(element, session.get_service("modeling_language"))
                tree_target = action_target(tree_menu, "Copiar ruta relativa")
                assert service._resolve(tree_target, True) == expected
                group.activate_action("copy-reference-name", GLib.Variant.new_string(tree_target))
                assert clipboard_text(window) == element.name
                labels = [e[0] for e in entries(session.get_service("tools_menu").menu)]
                assert "Propiedades…" in labels and "Importar/leer componente en crudo…" in labels
                captures.append((service, target, tree_target, expected, window, menu))

            first, second = captures
            for receiver, foreign in ((first, second), (second, first)):
                try:
                    receiver[0]._resolve(foreign[1], True)
                except ReferenceError:
                    pass
                else:
                    raise AssertionError("Foreign project target accepted")
            # Closing one service leaves other sessions functional.
            first[0].shutdown()
            assert second[0]._copy(second[1], True)
            assert clipboard_text(second[4]) == second[3]
            assert not any(e[0] == "Copiar nombre" for e in entries(first[5]))
            assert not errors, errors
    finally:
        for diagrams, window in opened:
            for diagram in list(diagrams.element_factory.select(UML.Diagram)):
                diagrams.close_diagram_page(diagram)
            diagrams.close()
            window.set_child(None)
            window.destroy()
        await settle()


with (output / f"{prefix}.txt").open("w", encoding="utf-8") as report:
    try:
        with contextlib.redirect_stdout(report), contextlib.redirect_stderr(report):
            logging.basicConfig(stream=report, level=logging.WARNING, force=True)
            from gi.repository import Gtk
            from gaphor.application import Session
            from gaphor.entrypoint import load_entry_points
            from gaphor.ui import diagrampage, modelbrowser
            from gaphor_copy_reference import CopyReferenceService
            from gaphor_description_editor import DescriptionEditor
            from gaphor_folder_diagram import FolderDiagramService
            if installed:
                from importlib.metadata import distributions
                records = list(distributions())
                for name, version in (("gaphor-copy-reference", "0.1.0"),
                                      ("gaphor-description-editor", "0.3.0"),
                                      ("gaphor-folder-diagram", "0.1.1")):
                    matches = [d for d in records if d.metadata["Name"] == name]
                    assert len(matches) == 1 and matches[0].version == version, (name, matches)
            Gtk.init()
            native_tree, native_controller = modelbrowser.popup_model, diagrampage.context_menu_controller
            native_copy = diagrampage.Clipboard.copy
            services = dict(load_entry_points("gaphor.services"))
            if not installed:
                services.update(copy_reference=CopyReferenceService,
                                description_editor=DescriptionEditor, folder_diagram=FolderDiagramService)
            # Session(services=...) filters entry-point names; it does not inject classes.
            def source_entries(scope, names=None):
                return dict(services) if scope == "gaphor.services" else load_entry_points(scope, names)
            loader = contextlib.nullcontext() if installed else patch(
                "gaphor.entrypoint.load_entry_points", side_effect=source_entries)
            with loader:
                first, second = Session(), Session()
            try:
                asyncio.run(verify((first, second)))
            finally:
                first.shutdown()
                second.shutdown()
            assert modelbrowser.popup_model is native_tree
            assert diagrampage.context_menu_controller is native_controller
            assert diagrampage.Clipboard.copy is native_copy
            report.write("PASS: portapapeles GTK, menús, hit testing, zoom, CSS, dos proyectos y coexistencia de tres plugins.\n")
        (output / f"{prefix}-status.txt").write_text("PASS", encoding="utf-8")
    except Exception:
        traceback.print_exc(file=report)
        (output / f"{prefix}-status.txt").write_text("FAIL", encoding="utf-8")
