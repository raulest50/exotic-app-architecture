"""Session-local orthogonal dependency tool for Gaphor 3.3.2."""

from importlib.metadata import version
import logging
from weakref import WeakKeyDictionary

from gi.repository import Gio, GLib
from gaphor.abc import ActionProvider, Service
from gaphor.core import action, event_handler, Transaction
from gaphor.core.modeling.event import ModelFlushed
from gaphor.diagram.diagramtoolbox import get_tool_def
from gaphor.event import Notification
from gaphor.ui import diagrampage
from gaphor.ui.event import CurrentDiagramChanged

from .interaction import install_drawing

log = logging.getLogger(__name__)
TITLE = "Conexiones ortogonales"
ACTION = "win.orthogonal-connections"
SUPPORTED_VERSION = "3.3.2"
_services = {}
_original_apply = None


def _apply(page, tool_name):
    service = _services.get(page.event_manager)
    if not service:
        return _original_apply(page, tool_name)
    if Transaction.in_transaction():
        return False
    service.pages[page] = tool_name
    for drawing in list(service.drawings):
        if drawing.view is page.view:
            drawing.close()
            service.drawings.discard(drawing)
    if service.enabled and tool_name == "toolbox-dependency" and page.view:
        tool = get_tool_def(page.modeling_language, tool_name)
        install_drawing(page, tool.item_factory, service)
        return True
    return _original_apply(page, tool_name)


class OrthogonalConnections(Service, ActionProvider):
    def __init__(self, tools_menu, event_manager):
        global _original_apply
        self.tools_menu = tools_menu
        self.events = event_manager
        self.enabled = False
        self.alive = True
        self.compatible = version("gaphor") == SUPPORTED_VERSION
        self.drawings = set()
        self.pages = WeakKeyDictionary()
        self.menu = None
        if not self.compatible:
            log.warning("Conexiones ortogonales requiere Gaphor %s", SUPPORTED_VERSION)
            return
        _services[event_manager] = self
        if _original_apply is None:
            _original_apply = diagrampage.DiagramPage.apply_tool_set
            diagrampage.DiagramPage.apply_tool_set = _apply
        if not hasattr(tools_menu, "exotic_custom_tools_menu"):
            tools_menu.exotic_custom_tools_menu = Gio.Menu.new()
            item = Gio.MenuItem.new_submenu("Custom tools", tools_menu.exotic_custom_tools_menu)
            item.set_attribute_value("x-exotic-custom-tools", GLib.Variant.new_boolean(True))
            tools_menu.menu.append_item(item)
        self.menu = tools_menu.exotic_custom_tools_menu
        self.menu.append(TITLE, ACTION)
        event_manager.subscribe(self._diagram_changed)
        event_manager.subscribe(self._flushed)

    @action(name="orthogonal-connections", label=TITLE, state=lambda self: self.enabled)
    def set_enabled(self, enabled):
        if not self.compatible or not self.alive:
            return
        self.cancel_drawings()
        self.enabled = bool(enabled)
        for page, tool in list(self.pages.items()):
            if page.view and tool == "toolbox-dependency":
                page.apply_tool_set(tool)
        if self.enabled:
            self.events.handle(Notification(
                "Dependencia (Shift+D): arrastra; Espacio fija un punto; "
                "Tab cambia el tramo; Escape cancela. Suelta sobre el destino."
            ))

    def cancel_drawings(self, except_drawing=None):
        for drawing in list(self.drawings):
            if drawing is not except_drawing:
                drawing.cancel()

    @event_handler(CurrentDiagramChanged)
    def _diagram_changed(self, event):
        for drawing in list(self.drawings):
            if drawing.view.model is not event.diagram:
                drawing.cancel()

    @event_handler(ModelFlushed)
    def _flushed(self, _event):
        self.cancel_drawings()

    def shutdown(self):
        global _original_apply
        if not self.alive:
            return
        self.set_enabled(False)
        self.alive = False
        for drawing in list(self.drawings):
            drawing.close()
        self.drawings.clear()
        self.pages.clear()
        self.events.unsubscribe(self._diagram_changed)
        self.events.unsubscribe(self._flushed)
        _services.pop(self.events, None)
        if not _services and _original_apply:
            if diagrampage.DiagramPage.apply_tool_set is _apply:
                diagrampage.DiagramPage.apply_tool_set = _original_apply
            _original_apply = None
        if self.menu:
            for index in reversed(range(self.menu.get_n_items())):
                attr = self.menu.get_item_attribute_value(index, "action", None)
                if attr and attr.get_string() == ACTION:
                    self.menu.remove(index)
            if not self.menu.get_n_items():
                for index in reversed(range(self.tools_menu.menu.get_n_items())):
                    if self.tools_menu.menu.get_item_attribute_value(index, "x-exotic-custom-tools", None):
                        self.tools_menu.menu.remove(index)
                if getattr(self.tools_menu, "exotic_custom_tools_menu", None) is self.menu:
                    del self.tools_menu.exotic_custom_tools_menu
