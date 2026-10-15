"""Real Gaphor sessions, native actions, persistence and plugin coexistence."""
import asyncio
import contextlib
import json
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
    for directory in ("gaphor-orthogonal-connections", "gaphor-description-editor", "gaphor-folder-diagram"):
        sys.path.insert(0, str(plugins / directory))
output = Path(os.environ["GAPHOR_ORTHOGONAL_TEST_OUTPUT"])
prefix = "installed-plugin-" if installed else "integration-"


async def settle():
    from gi.repository import GLib
    for _ in range(3):
        while GLib.MainContext.default().pending():
            GLib.MainContext.default().iteration(False)
        await asyncio.sleep(0.01)


async def verify(sessions):
    from gi.repository import Gdk, GLib, Gtk
    from gaphas.tool.zoom import on_scroll
    from gaphor import UML
    from gaphor.core import Transaction
    from gaphor.diagram.event import DiagramOpened
    from gaphor.storage.save import save
    from gaphor.UML.classes.package import PackageItem
    from gaphor.UML.classes.component import ComponentItem
    from gaphor.UML.deployments.artifact import ArtifactItem
    from gaphor.ui.actiongroup import window_action_group
    from gaphor.ui.diagrams import get_widgets_on_pages
    from gaphor_description_editor.model import save_properties

    errors = []
    opened = []
    records = []
    asyncio.get_running_loop().set_exception_handler(lambda _loop, error: errors.append(error))
    try:
        with patch("sys.excepthook", side_effect=lambda *error: errors.append(error)):
            for number, session in enumerate(sessions):
                service = session.get_service("orthogonal_connections")
                editor = session.get_service("description_editor")
                importer = session.get_service("folder_diagram")
                assert not service.enabled and service.compatible
                model = session.get_service("element_factory")
                events = session.get_service("event_manager")
                diagrams = session.get_service("diagrams")
                window = Gtk.Window()
                session.get_service("main_window").window = window
                window.set_child(diagrams.open())
                actions = window_action_group(session.component_registry)
                window.insert_action_group("win", actions)
                opened.append((diagrams, window))
                with Transaction(events):
                    diagram = model.create_as(UML.ComponentDiagram, "same-diagram")
                    diagram.name = "Temporal"
                    items = []
                    for index, (cls, item_cls) in enumerate(((UML.Artifact, ArtifactItem),
                                                            (UML.Component, ComponentItem),
                                                            (UML.Package, PackageItem))):
                        subject = model.create(cls)
                        subject.name = f"Elemento {index}"
                        item = diagram.create(item_cls, subject=subject)
                        item.width, item.height = 170, 100
                        item.matrix.translate(60 + index * 270, 70 + index * 140)
                        items.append(item)
                events.handle(DiagramOpened(diagram))
                await settle()
                page = next(widget.diagram_page for _, widget in get_widgets_on_pages(diagrams._notebook))
                # Native menu action must be a stateful toggle.
                actions.change_action_state("orthogonal-connections", GLib.Variant.new_boolean(True))
                assert service.enabled
                assert actions.get_action_state("orthogonal-connections").get_boolean()
                page.select_tool("toolbox-dependency")
                view = page.view
                for source, target in zip(items, items[1:]):
                    drawing = next(d for d in service.drawings if not d.closed)
                    start = view.get_matrix_i2v(source).transform_point(source.width, 35)
                    end = view.get_matrix_i2v(target).transform_point(0, 35)
                    fake = SimpleNamespace(set_state=lambda _: None)
                    drawing._begin(fake, *start)
                    assert drawing.tx
                    drawing.move(((start[0] + end[0]) / 2, end[1] - 40))
                    drawing.keys.emit("key-pressed", Gdk.KEY_space, 32, Gdk.ModifierType(0))
                    drawing.keys.emit("key-released", Gdk.KEY_space, 32, Gdk.ModifierType(0))
                    line = drawing.item
                    assert drawing.finish(end)
                    assert source.subject in line.subject.client
                    assert target.subject in line.subject.supplier
                    await settle()
                    # The session may reset the toolbox after DiagramItemPlaced.
                    page.select_tool("toolbox-dependency")
                controller = SimpleNamespace(get_widget=lambda: view, get_current_event_state=lambda: Gdk.ModifierType.CONTROL_MASK)
                assert on_scroll(controller, 0, -1)
                save_properties(items[0].subject, "Documentación temporal", "Nota", "color: navy;", events)
                await settle()
                assert importer.focused is not None
                editor.open_element(items[0].subject)
                assert editor.editor
                editor.editor.cancel()
                await settle()
                assert service.enabled
                records.append((service, diagram))
                if number == 0:
                    from gaphor.UML.classes.dependency import DependencyItem
                    expected = {item.id: [tuple(map(float, handle.pos)) for handle in item.handles()]
                                for item in diagram.get_all_items() if isinstance(item, DependencyItem)}
                    with (output / "portable.gaphor").open("w", encoding="utf-8") as stream:
                        save(stream, model)
                    (output / "geometry.json").write_text(json.dumps(expected), encoding="utf-8")
            records[0][0].shutdown()
            assert records[1][0].enabled
            assert not errors, errors
    finally:
        for diagrams, window in opened:
            for diagram in list(diagrams.element_factory.select(UML.Diagram)):
                diagrams.close_diagram_page(diagram)
            diagrams.close()
            window.set_child(None)
            window.destroy()
        await settle()


with (output / f"{prefix}results.txt").open("w", encoding="utf-8") as report:
    try:
        with contextlib.redirect_stdout(report), contextlib.redirect_stderr(report):
            logging.basicConfig(stream=report, level=logging.WARNING, force=True)
            from gi.repository import Gtk
            from gaphor.application import Session
            from gaphor.entrypoint import load_entry_points
            from gaphor.ui.diagrampage import DiagramPage
            from gaphor_orthogonal_connections import OrthogonalConnections
            from gaphor_description_editor import DescriptionEditor
            from gaphor_folder_diagram import FolderDiagramService
            if installed:
                from importlib.metadata import distributions
                records = list(distributions())
                for name, version in (("gaphor-orthogonal-connections", "0.1.0"),
                                      ("gaphor-description-editor", "0.3.0"),
                                      ("gaphor-folder-diagram", "0.1.1")):
                    found = [d for d in records if d.metadata["Name"] == name]
                    assert len(found) == 1 and found[0].version == version, (name, found)
            Gtk.init()
            native = DiagramPage.apply_tool_set
            services = dict(load_entry_points("gaphor.services"))
            services.update(orthogonal_connections=OrthogonalConnections,
                            description_editor=DescriptionEditor, folder_diagram=FolderDiagramService)
            def source_entries(scope, names=None):
                return dict(services) if scope == "gaphor.services" else load_entry_points(scope, names)
            with (contextlib.nullcontext() if installed else patch("gaphor.entrypoint.load_entry_points", side_effect=source_entries)):
                first, second = Session(), Session()
            try:
                asyncio.run(verify((first, second)))
            finally:
                first.shutdown()
                second.shutdown()
            assert DiagramPage.apply_tool_set is native
            report.write("PASS: menús nativos, dos sesiones, tres tipos UML, CSS, zoom, Propiedades, importador y persistencia.\n")
        (output / f"{prefix}status.txt").write_text("PASS", encoding="utf-8")
    except Exception:
        traceback.print_exc(file=report)
        (output / f"{prefix}status.txt").write_text("FAIL", encoding="utf-8")
