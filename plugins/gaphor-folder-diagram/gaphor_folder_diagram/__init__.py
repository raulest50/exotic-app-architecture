"""Independent Gaphor session plugin: Tools > Custom tools > raw component."""

from importlib.metadata import version
import logging

from gi.repository import Gio, GLib, Gtk
from gaphor.abc import ActionProvider, Service
from gaphor.core import action, event_handler
from gaphor.core.modeling.event import ModelFlushed, ModelReady
from gaphor.diagram.event import DiagramOpened, DiagramSelectionChanged
from gaphor.ui.event import CurrentDiagramChanged, ModelSelectionChanged

from .model import nearest_package
from .ui import ImportWindow, TITLE

log = logging.getLogger(__name__)
ACTION = "win.import-raw-component"


class FolderDiagramService(Service, ActionProvider):
    def __init__(self, main_window, tools_menu, event_manager, element_factory, diagrams):
        self.main_window = main_window
        self.tools_menu = tools_menu
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.diagrams = diagrams
        self.focused = None
        self.window = None
        self.fit_source = 0
        self.compatible = version("gaphor") == "3.3.2"
        self.alive = True
        # Other independent custom tools can reuse this session-local Gio.Menu.
        if not hasattr(tools_menu, "exotic_custom_tools_menu"):
            tools_menu.exotic_custom_tools_menu = Gio.Menu.new()
            item = Gio.MenuItem.new_submenu("Custom tools", tools_menu.exotic_custom_tools_menu)
            item.set_attribute_value("x-exotic-custom-tools", GLib.Variant.new_boolean(True))
            tools_menu.menu.append_item(item)
        self.menu = tools_menu.exotic_custom_tools_menu
        self.menu.append(TITLE, ACTION)
        for handler in (self._model_selection, self._diagram_selection, self._diagram_changed, self._reset):
            event_manager.subscribe(handler)

    @event_handler(ModelSelectionChanged)
    def _model_selection(self, event):
        self.focused = event.focused_element

    @event_handler(DiagramSelectionChanged)
    def _diagram_selection(self, event):
        self.focused = event.focused_item
        if self.focused is None:
            self.focused = getattr(event.diagram_view, "model", None)

    @event_handler(CurrentDiagramChanged)
    def _diagram_changed(self, event):
        self.focused = event.diagram

    @event_handler(ModelFlushed, ModelReady)
    def _reset(self, _event):
        self.focused = None
        if self.window:
            self.window.cancel()

    @action(name="import-raw-component", label=TITLE)
    def import_raw_component(self):
        if not self.compatible:
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window, modal=True,
                message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.CLOSE,
                text="Este plugin requiere Gaphor 3.3.2.",
            )
            dialog.connect("response", lambda widget, _response: widget.destroy())
            dialog.present()
            return
        if self.window:
            self.window.present()
            return
        self.window = ImportWindow(
            self.main_window.window, self.element_factory, self.event_manager,
            nearest_package(self.focused), self._created, self._closed,
        )
        self.window.present()

    def _closed(self, window):
        if self.window is window:
            self.window = None

    def _created(self, capture):
        try:
            self.event_manager.handle(DiagramOpened(capture.diagram))
        except Exception:
            log.exception("Captura creada; no se pudo abrir automáticamente el diagrama")
            return
        if self.fit_source:
            GLib.source_remove(self.fit_source)
        attempts = 0

        def fit():
            nonlocal attempts
            attempts += 1
            if not self.alive or self.diagrams.get_current_diagram() is not capture.diagram:
                self.fit_source = 0
                return GLib.SOURCE_REMOVE
            view = self.diagrams.get_current_view()
            if view is None or view.get_width() < 100 or view.get_height() < 100:
                if attempts < 20:
                    return GLib.SOURCE_CONTINUE
            else:
                root = capture.root_item
                x, y = root.matrix.transform_point(0, 0)
                width, height = view.get_width(), view.get_height()
                scale = min(1.0, (width - 80) / root.width, (height - 100) / root.height)
                view.matrix.set(scale, 0, 0, scale,
                                (width - root.width * scale) / 2 - x * scale,
                                (height - root.height * scale) / 2 - y * scale + 12)
                view.queue_draw()
            self.fit_source = 0
            return GLib.SOURCE_REMOVE

        self.fit_source = GLib.timeout_add(50, fit)

    def shutdown(self):
        self.alive = False
        if self.window:
            self.window.cancel()
        if self.fit_source:
            GLib.source_remove(self.fit_source)
            self.fit_source = 0
        for handler in (self._model_selection, self._diagram_selection, self._diagram_changed, self._reset):
            self.event_manager.unsubscribe(handler)
        for index in reversed(range(self.menu.get_n_items())):
            attribute = self.menu.get_item_attribute_value(index, "action", None)
            if attribute and attribute.get_string() == ACTION:
                self.menu.remove(index)
        if not self.menu.get_n_items():
            menu = self.tools_menu.menu
            for index in reversed(range(menu.get_n_items())):
                if menu.get_item_attribute_value(index, "x-exotic-custom-tools", None):
                    menu.remove(index)
            if getattr(self.tools_menu, "exotic_custom_tools_menu", None) is self.menu:
                del self.tools_menu.exotic_custom_tools_menu
