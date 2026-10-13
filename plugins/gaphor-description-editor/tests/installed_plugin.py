"""Exercise entry points, session services, menu, accelerators and save after installation."""

import contextlib
from importlib.metadata import distribution
import logging
import os
from pathlib import Path
import traceback

output = Path(os.environ["GAPHOR_DESCRIPTION_TEST_OUTPUT"])


def menu_labels(menu):
    for index in range(menu.get_n_items()):
        if label := menu.get_item_attribute_value(index, "label", None):
            yield label.get_string()
        for link in ("section", "submenu"):
            if child := menu.get_item_link(index, link):
                yield from menu_labels(child)


with (output / "installed-plugin.txt").open("w", encoding="utf-8") as report:
    try:
        with contextlib.redirect_stdout(report), contextlib.redirect_stderr(report):
            logging.basicConfig(stream=report, level=logging.WARNING, force=True)
            from gi.repository import Gtk
            from gaphor import UML
            from gaphor.application import Session
            from gaphor.core import Transaction
            from gaphor.diagram.tools import textedit
            from gaphor.entrypoint import load_entry_points
            from gaphor.ui.actiongroup import apply_shortcuts_from_entry_point, window_action_group
            from gaphor.ui.event import ModelSelectionChanged
            from gaphor_description_editor import DescriptionPropertyPage
            from gaphor_description_editor.model import read_description

            Gtk.init()
            native = textedit.instant_editor
            assert distribution("gaphor-description-editor").version == "0.1.0"
            assert "description_editor" in load_entry_points("gaphor.services")
            first, second = Session(), Session()
            try:
                for index, session in enumerate((first, second)):
                    # Supply a native window without opening the user's workspace.
                    session.get_service("main_window").window = Gtk.Window()
                    service = session.get_service("description_editor")
                    assert service.compatible
                    model = session.get_service("element_factory")
                    events = session.get_service("event_manager")
                    with Transaction(events):
                        component = model.create(UML.Component)
                        component.name = f"Proyecto temporal {index}"
                        component.note = f"Nota {index}"
                    events.handle(ModelSelectionChanged(None, component))
                    menu = session.get_service("tools_menu").menu
                    labels = list(menu_labels(menu))
                    assert "Editar descripción" in labels, labels
                    group = window_action_group(session.component_registry)
                    assert group.has_action("edit-description")
                    group.activate_action("edit-description", None)
                    assert service.editor.subject is component
                    service.editor.description_buffer.set_text(f"Descripción {index}")
                    assert service.editor.save()
                    assert read_description(component) == f"Descripción {index}"
                    assert component.note == f"Nota {index}"
                    page = DescriptionPropertyPage(component, events)
                    assert page.construct() is not None
                    assert page.preview.get_text() == f"Descripción {index}"
                    page.close()
                app = Gtk.Application(application_id="org.gaphor.DescriptionEditorTests")
                apply_shortcuts_from_entry_point("gaphor.services", "win", app)
                assert app.get_accels_for_action("win.edit-description") == ["<Control><Alt>d"]
            finally:
                first.shutdown()
                second.shutdown()
            assert textedit.instant_editor is native
            report.write("PASS: instalación detectada; menú, Ctrl+Alt+D, panel, guardado y dos sesiones independientes.\n")
            (output / "installed-plugin-status.txt").write_text("PASS", encoding="utf-8")
    except Exception:
        traceback.print_exc(file=report)
        (output / "installed-plugin-status.txt").write_text("FAIL", encoding="utf-8")
