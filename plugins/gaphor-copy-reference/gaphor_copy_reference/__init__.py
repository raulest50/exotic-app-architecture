"""Session-local copy actions; temporary adapters for Gaphor 3.3.2 context menus."""

from importlib.metadata import version
import json
import logging
from uuid import uuid4
from weakref import WeakKeyDictionary, WeakSet, ref

from gi.repository import Gdk, Gio, GLib, Gtk
from gaphor.abc import ActionProvider, Service
from gaphor.core import action
from gaphor.event import Notification
from gaphor.transaction import Transaction
from gaphor.ui import diagrampage, modelbrowser

from .paths import ReferenceError, diagram_path, element_name, tree_path

log = logging.getLogger(__name__)
SUPPORTED_VERSION = "3.3.2"
_services = {}
_original_tree_popup = None
_original_diagram_controller = None
_MARKER = "x-exotic-copy-reference"


def _service(model):
    service = _services.get(id(model))
    return service if service and service.element_factory is model and service.alive else None


def _tree_popup(element, modeling_language):
    menu = _original_tree_popup(element, modeling_language)
    if service := _service(getattr(element, "model", None)):
        service.extend_menu(menu, element)
    return menu


def _diagram_controller(context_menu, diagram):
    if service := _service(diagram.model):
        # Populate BEFORE popup(): opening the native popover can end the gesture,
        # so a connect_after handler cannot reliably inspect its GDK event.
        controller = Gtk.GestureClick.new()
        controller.set_button(0)
        handler = controller.connect(
            "pressed", service.on_context_pressed, context_menu, diagram,
        )
        service.controllers[controller] = (handler, ref(context_menu), diagram)
        return controller
    return _original_diagram_controller(context_menu, diagram)


def _install_hooks():
    global _original_tree_popup, _original_diagram_controller
    if _original_tree_popup is None:
        _original_tree_popup = modelbrowser.popup_model
        _original_diagram_controller = diagrampage.context_menu_controller
        modelbrowser.popup_model = _tree_popup
        diagrampage.context_menu_controller = _diagram_controller


def _remove_hooks():
    global _original_tree_popup, _original_diagram_controller
    if not _services and _original_tree_popup is not None:
        if modelbrowser.popup_model is _tree_popup:
            modelbrowser.popup_model = _original_tree_popup
        if diagrampage.context_menu_controller is _diagram_controller:
            diagrampage.context_menu_controller = _original_diagram_controller
        _original_tree_popup = _original_diagram_controller = None


class CopyReferenceService(Service, ActionProvider):
    def __init__(self, main_window, event_manager, element_factory, diagrams):
        self.main_window = main_window
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.diagrams = diagrams
        self.token = str(uuid4())
        self.alive = True
        self.compatible = version("gaphor") == SUPPORTED_VERSION
        self.controllers = WeakKeyDictionary()
        self.menus = WeakSet()
        if self.compatible:
            _services[id(element_factory)] = self
            _install_hooks()

    def extend_menu(self, menu, element, item=None, diagram=None):
        if not self.alive or not self.compatible:
            return
        try:
            element_name(element, self.element_factory)
        except ReferenceError:
            return
        # GTK may request the same menu more than once during a popup lifecycle.
        for index in reversed(range(menu.get_n_items())):
            if menu.get_item_attribute_value(index, _MARKER, None):
                menu.remove(index)
        target = json.dumps({
            "session": self.token, "element": element.id,
            "diagram": diagram.id if diagram else None,
            "item": item.id if item else None,
        })
        section = Gio.Menu.new()
        for label, action_name in (
            ("Copiar nombre", "win.copy-reference-name"),
            ("Copiar ruta relativa", "win.copy-reference-path"),
        ):
            entry = Gio.MenuItem.new(label, action_name)
            entry.set_attribute_value("target", GLib.Variant.new_string(target))
            section.append_item(entry)
        entry = Gio.MenuItem.new_section(None, section)
        entry.set_attribute_value(_MARKER, GLib.Variant.new_boolean(True))
        menu.append_item(entry)
        self.menus.add(menu)

    def on_context_pressed(self, controller, _press_count, x, y, context_menu, diagram):
        if not self.alive or Transaction.in_transaction():
            return
        event = controller.get_last_event()
        if event is None or not event.triggers_context_menu():
            return
        view = controller.get_widget()
        if view is None or view.model is not diagram:
            return
        item, _handle = diagrampage.default_find_item_and_handle_at_point(view, (x, y))
        subject = item.subject if item and item.subject else diagram
        # Preserve the native menu, including its blank-canvas behavior.
        menu = diagrampage.popup_model(subject)
        if item is not None and item.subject is not None:
            self.extend_menu(menu, item.subject, item, diagram)
        context_menu.set_menu_model(menu)
        rect = Gdk.Rectangle()
        rect.x, rect.y, rect.width, rect.height = int(x), int(y), 1, 1
        context_menu.set_has_arrow(False)
        context_menu.set_pointing_to(rect)
        context_menu.popup()

    @action(name="copy-reference-name", label="Copiar nombre")
    def copy_name(self, target: str):
        self._copy(target, path=False)

    @action(name="copy-reference-path", label="Copiar ruta relativa")
    def copy_path(self, target: str):
        self._copy(target, path=True)

    def _resolve(self, target, path):
        if not self.alive or not self.compatible:
            raise ReferenceError("Copiar referencias requiere Gaphor 3.3.2 y un proyecto abierto.")
        try:
            data = json.loads(target)
            if not isinstance(data, dict) or data.get("session") != self.token:
                raise ValueError("Wrong session")
            element = self.element_factory.lookup(data["element"])
        except (TypeError, ValueError, KeyError):
            raise ReferenceError("La referencia ya no corresponde a este proyecto.") from None
        name = element_name(element, self.element_factory)
        if data.get("diagram") is not None:
            diagram = self.element_factory.lookup(data["diagram"])
            if diagram is None or diagram is not self.diagrams.get_current_diagram():
                raise ReferenceError("El diagrama activo cambió. Abre nuevamente el menú de la figura.")
            item = next((candidate for candidate in diagram.get_all_items()
                         if candidate.id == data.get("item") and candidate.subject is element), None)
            if item is None:
                raise ReferenceError("La figura ya no está disponible en el diagrama.")
            return diagram_path(item, diagram, self.element_factory) if path else name
        return tree_path(element, self.diagrams.get_current_diagram(), self.element_factory) if path else name

    def _copy(self, target, path):
        if not self.alive:
            return False
        try:
            text = self._resolve(target, path)
            window = self.main_window.window
            if window is None:
                raise ReferenceError("No hay una ventana disponible para copiar la referencia.")
            clipboard = window.get_clipboard()
            if not clipboard.set_content(Gdk.ContentProvider.new_for_value(text)):
                raise ReferenceError("No se pudo copiar al portapapeles.")
        except ReferenceError as error:
            self.event_manager.handle(Notification(str(error)))
            return False
        except Exception:
            log.exception("No se pudo copiar la referencia")
            self.event_manager.handle(Notification("No se pudo copiar la referencia. Consulta el registro de Gaphor."))
            return False
        self.event_manager.handle(Notification("Copiado"))
        return True

    def shutdown(self):
        if not self.alive:
            return
        self.alive = False
        for controller, (handler, menu_ref, diagram) in list(self.controllers.items()):
            if controller.handler_is_connected(handler):
                controller.disconnect(handler)
            if view := controller.get_widget():
                view.remove_controller(controller)
                if context_menu := menu_ref():
                    view.add_controller(_original_diagram_controller(context_menu, diagram))
        self.controllers.clear()
        for menu in list(self.menus):
            for index in reversed(range(menu.get_n_items())):
                if menu.get_item_attribute_value(index, _MARKER, None):
                    menu.remove(index)
        self.menus.clear()
        if _services.get(id(self.element_factory)) is self:
            _services.pop(id(self.element_factory))
        _remove_hooks()
