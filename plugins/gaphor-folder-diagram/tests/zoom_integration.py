"""Exercise native diagram views and Ctrl+wheel handling in temporary sessions."""

import asyncio
from types import SimpleNamespace
from unittest.mock import patch

from gi.repository import Gdk, GLib
from gaphas.tool.zoom import on_scroll
from gaphor import UML
from gaphor.core.modeling import StyleSheet
from gaphor.core.modeling.diagram import StyledItem
from gaphor.diagram.event import DiagramOpened, DiagramSelectionChanged
from gaphor_description_editor.model import read_css, save_properties
from gaphor_folder_diagram.model import nearest_package


async def drain():
    context = GLib.MainContext.default()
    # Gaphas updates views in asyncio tasks; CSS refresh uses GLib idle callbacks.
    for _ in range(3):
        while context.pending():
            context.iteration(False)
        await asyncio.sleep(0.01)


def exercise_zoom(session, capture, css):
    """Use the real scroll callback; only the OS modifier state is supplied."""
    return asyncio.run(_exercise_zoom(session, capture, css))


async def _exercise_zoom(session, capture, css):
    events = session.get_service("event_manager")
    importer = session.get_service("folder_diagram")
    editor = session.get_service("description_editor")
    diagrams = session.get_service("diagrams")
    window = session.get_service("main_window").window
    uncaught = []
    asyncio.get_running_loop().set_exception_handler(lambda _loop, error: uncaught.append(error))

    try:
        with patch("sys.excepthook", side_effect=lambda *error: uncaught.append(error)):
            window.set_child(diagrams.open())
            events.handle(DiagramOpened(capture.diagram))
            view = diagrams.get_current_view()
            assert view.model is capture.diagram
            item = next(i for i in capture.diagram.get_all_items()
                        if isinstance(i.subject, UML.Artifact))
            controller = SimpleNamespace(
                get_widget=lambda: view,
                get_current_event_state=lambda: Gdk.ModifierType.CONTROL_MASK,
            )
            for selected in (item, None):
                view.selection.unselect_all()
                view.selection.focused_item = selected
                events.handle(DiagramSelectionChanged(view, selected, view.selection.selected_items))
                await drain()
                assert importer.focused is (selected if selected is not None else capture.diagram)
                expected = item.subject.package if selected is not None else capture.package
                assert nearest_package(importer.focused) is expected
                scale = view.matrix[0]
                assert on_scroll(controller, 0, -1)
                assert view.matrix[0] > scale
                scale = view.matrix[0]
                assert on_scroll(controller, 0, 1)
                assert view.matrix[0] < scale
                await drain()

            # Trigger the same asynchronous refresh that exposed the importer error.
            save_properties(item.subject, "Descripción", "Nota", css, events)
            assert editor.style_runtime.pending
            await drain()
            assert not editor.style_runtime.pending
            assert read_css(item.subject) == css
            events.handle(DiagramSelectionChanged(view, None, view.selection.selected_items))
            assert importer.focused is capture.diagram
            assert nearest_package(importer.focused) is capture.package
            sheet = item.model.style_sheet or StyleSheet()
            color = sheet.compute_style(StyledItem(item))["color"]
            assert not uncaught, uncaught
            return item, color
    finally:
        diagrams.close_diagram_page(capture.diagram)
        diagrams.close()
        window.set_child(None)


def assert_style_isolation(first, second):
    assert first[0].model is not second[0].model
    assert first[1] != second[1]
    for item, color in (first, second):
        sheet = item.model.style_sheet or StyleSheet()
        assert sheet.compute_style(StyledItem(item))["color"] == color
