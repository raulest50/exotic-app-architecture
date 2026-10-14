"""Native tab navigation in two temporary Gaphor sessions, with both plugins."""

import asyncio
from unittest.mock import patch

from gi.repository import GLib, Gtk
from gaphor import UML
from gaphor.core import Transaction
from gaphor.diagram.event import DiagramOpened


async def settle():
    context = GLib.MainContext.default()
    for _ in range(3):
        while context.pending():
            context.iteration(False)
        await asyncio.sleep(0.01)


def verify_navigation(sessions):
    asyncio.run(_verify_navigation(sessions))


async def _verify_navigation(sessions):
    opened = []
    errors = []
    asyncio.get_running_loop().set_exception_handler(lambda _loop, error: errors.append(error))
    try:
        with patch("sys.excepthook", side_effect=lambda *error: errors.append(error)):
            for session in sessions:
                editor = session.get_service("description_editor")
                importer = session.get_service("folder_diagram")
                assert editor.compatible and importer.compatible
                main_window = session.get_service("main_window")
                main_window.window = main_window.window or Gtk.Window()
                diagrams = session.get_service("diagrams")
                main_window.window.set_child(diagrams.open())
                opened.append(diagrams)
                model = session.get_service("element_factory")
                events = session.get_service("event_manager")
                with Transaction(events):
                    artifact = model.create(UML.Artifact)
                    artifact.name = "archivo.ts"
                    # Deliberately equal names and identifiers in different models.
                    child = model.create_as(UML.ActivityDiagram, "navigation-child")
                    child.name = "Flujo"
                    child.element = artifact
                    other = model.create_as(UML.ComponentDiagram, "navigation-other")
                    other.name = "Otra vista"
                    other.element = artifact
                events.handle(DiagramOpened(child))
                events.handle(DiagramOpened(other))
                await settle()
                count = diagrams._notebook.get_n_pages()
                assert count == 2
                profiles = {p.id for p in model.select(UML.Profile)}
                editor.open_element(artifact)
                window = editor.editor
                window.tabs.set_current_page(window.tabs.page_num(window.diagrams_page))
                window.diagrams_page.listbox.select_row(window.diagrams_page.listbox.get_row_at_index(0))
                window.diagrams_page.open_button.emit("clicked")
                await settle()
                assert window.finished and editor.editor is None
                assert diagrams.get_current_diagram() is child
                assert diagrams._notebook.get_n_pages() == count
                assert {p.id for p in model.select(UML.Profile)} == profiles, "Browsing must not create documentation data"
                assert importer.focused is child
                if len(opened) == 1:
                    diagrams.set_current_diagram(other)
            assert opened[0].get_current_diagram().id == "navigation-other"
            assert opened[1].get_current_diagram().id == "navigation-child"
            assert not errors, errors
    finally:
        for diagrams in opened:
            for diagram in list(diagrams.element_factory.select(UML.Diagram)):
                diagrams.close_diagram_page(diagram)
            diagrams.close()
        await settle()
