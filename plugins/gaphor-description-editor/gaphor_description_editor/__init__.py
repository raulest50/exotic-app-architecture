"""Gaphor 3.3.2 properties: documentation, child diagrams and per-element CSS."""

import logging
from importlib.metadata import version

from gi.repository import Gdk, GLib, Gtk, Pango

from gaphor import UML
from gaphor.abc import ActionProvider, Service
from gaphor.core import action, event_handler
from gaphor.core.modeling.event import ModelReady
from gaphor.diagram.event import DiagramOpened, DiagramSelectionChanged
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages
from gaphor.diagram.tools import textedit
from gaphor.ui.event import CurrentDiagramChanged, ModelSelectionChanged

from .model import DocumentationError, read_css, read_description, save_documentation, save_properties, target_element
from .styles import CssError, StyleRuntime
from .diagrams import DiagramList

log = logging.getLogger(__name__)
SUPPORTED_VERSION = "3.3.2"
_services = {}
_original_instant_editor = None


def _route_instant_editor(item, view, event_manager, pos=None):
    """Only the positional (double-click) path changes; F2 delegates unchanged."""
    service = _services.get(event_manager)
    if pos is not None and service and target_element(item) is not None:
        service.open_element(item)
        return True
    return _original_instant_editor(item, view, event_manager, pos)


def _install_hook():
    global _original_instant_editor
    if _original_instant_editor is None:
        _original_instant_editor = textedit.instant_editor
        textedit.instant_editor = _route_instant_editor


def _remove_hook():
    global _original_instant_editor
    if not _services and _original_instant_editor is not None:
        if textedit.instant_editor is _route_instant_editor:
            textedit.instant_editor = _original_instant_editor
        _original_instant_editor = None


def _buffer_text(buffer):
    return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)


class DocumentationWindow(Gtk.Window):
    def __init__(self, parent, subject, event_manager, on_closed):
        super().__init__(
            title=f"Propiedades — {getattr(subject, 'name', '') or type(subject).__name__}",
            transient_for=parent,
            modal=True,
            resizable=True,
            default_width=900,
            default_height=650,
        )
        self.subject = subject
        self.model = subject.model
        self.event_manager = event_manager
        self.on_closed = on_closed
        self.initial = (read_description(subject), subject.note or "", read_css(subject))
        self.finished = False
        self.confirmation = None

        header = Gtk.HeaderBar()
        cancel = Gtk.Button(label="Cancelar")
        cancel.connect("clicked", lambda _button: self.cancel())
        save = Gtk.Button(label="Guardar")
        save.add_css_class("suggested-action")
        save.connect("clicked", lambda _button: self.save())
        header.pack_start(cancel)
        header.pack_end(save)
        self.set_titlebar(header)

        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        for side in ("top", "bottom", "start", "end"):
            getattr(layout, f"set_margin_{side}")(16)
        self.paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL, vexpand=True, wide_handle=True)
        description, self.description_buffer, description_view = self._field("Descripción", self.initial[0])
        note, self.note_buffer, _note_view = self._field("Nota", self.initial[1])
        self.paned.set_start_child(description)
        self.paned.set_end_child(note)
        self.paned.set_shrink_start_child(False)
        self.paned.set_shrink_end_child(False)
        self.paned.set_position(350)
        self.tabs = Gtk.Notebook(vexpand=True)
        self.tabs.append_page(self.paned, Gtk.Label(label="Documentación"))
        self.diagrams_page = DiagramList(subject, self.open_child_diagram)
        self.tabs.append_page(self.diagrams_page, Gtk.Label(label="Diagramas"))
        css_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.css_page = css_box
        css_box.append(Gtk.Label(
            label="Se aplica a este elemento en todos los diagramas. Las figuras internas conservan su propio estilo.",
            xalign=0, wrap=True,
        ))
        css_field, self.css_buffer, self.css_view = self._field("Estilo CSS", self.initial[2], code=True)
        css_box.append(css_field)
        css_help = Gtk.Label(
            label="Ejemplo: background-color: lightblue; color: navy; font-size: 14;\n"
                  "Solo declaraciones, sin selectores ni llaves. Vacía el campo para recuperar el estilo normal.\n"
                  "El texto CSS se conserva en el proyecto; su apariencia requiere este plugin.",
            xalign=0, wrap=True, selectable=True,
        )
        css_help.add_css_class("dim-label")
        css_box.append(css_help)
        self.tabs.append_page(css_box, Gtk.Label(label="Estilo CSS"))
        self.tabs.connect("switch-page", self._switch_page)
        layout.append(self.tabs)
        hint = Gtk.Label(label="Los cambios se incorporan al modelo. Guarda después el proyecto como de costumbre.", xalign=0, wrap=True)
        hint.add_css_class("dim-label")
        layout.append(hint)
        self.error = Gtk.Label(xalign=0, wrap=True, visible=False)
        self.error.add_css_class("error")
        layout.append(self.error)
        self.set_child(layout)
        self.set_focus(description_view)
        self.connect("close-request", self._close_request)
        keys = Gtk.EventControllerKey.new()
        keys.connect("key-pressed", self._key_pressed)
        self.add_controller(keys)

    @staticmethod
    def _field(title, text, code=False):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, vexpand=True)
        label = Gtk.Label(label=title, xalign=0)
        label.add_css_class("heading")
        box.append(label)
        buffer = Gtk.TextBuffer()
        buffer.set_text(text)
        view = Gtk.TextView(
            buffer=buffer, wrap_mode=Gtk.WrapMode.NONE if code else Gtk.WrapMode.WORD_CHAR,
            monospace=code,
            top_margin=12, bottom_margin=12, left_margin=12, right_margin=12,
        )
        label.set_mnemonic_widget(view)
        scroll = Gtk.ScrolledWindow(vexpand=True, min_content_height=100)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC if code else Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(view)
        frame = Gtk.Frame(child=scroll)
        box.append(frame)
        return box, buffer, view

    def _values(self):
        return tuple(_buffer_text(buffer) for buffer in
                     (self.description_buffer, self.note_buffer, self.css_buffer))

    def _show_error(self, message):
        self.error.set_text(message)
        self.error.set_visible(True)

    def _save_fields(self):
        try:
            save_properties(
                self.subject, *self._values(),
                self.event_manager, expected=self.initial,
            )
        except DocumentationError as error:
            if isinstance(error, CssError):
                self.tabs.set_current_page(self.tabs.page_num(self.css_page))
            self._show_error(str(error))
            return False
        except Exception:
            log.exception("No se pudieron guardar las propiedades")
            self._show_error("No se pudo guardar. Conserva tu texto y consulta el registro de Gaphor.")
            return False
        self.initial = self._values()
        return True

    def save(self):
        if self.finished or not self._save_fields():
            return False
        self.cancel()
        return True

    def _switch_page(self, _tabs, page, _number):
        if page is self.diagrams_page:
            self.diagrams_page.refresh()

    def _valid_diagram(self, diagram):
        if self.finished:
            return False
        if (self.model.lookup(self.subject.id) is not self.subject
                or not isinstance(diagram, UML.Diagram)
                or self.model.lookup(diagram.id) is not diagram
                or diagram.element is not self.subject):
            self._show_error("El diagrama fue eliminado o ya no pertenece directamente a este elemento.")
            self.diagrams_page.refresh()
            return False
        return True

    def open_child_diagram(self, diagram):
        if not self._valid_diagram(diagram):
            return False
        if self.confirmation:
            self.confirmation.present()
            return False
        if self._values() == self.initial:
            return self._navigate(diagram)
        dialog = Gtk.MessageDialog(
            transient_for=self, modal=True, message_type=Gtk.MessageType.QUESTION,
            text="¿Guardar los cambios antes de abrir el diagrama?",
            secondary_text="Los cambios se incorporarán al modelo. El archivo se guarda después con Ctrl+S.",
        )
        dialog.add_buttons("Cancelar", Gtk.ResponseType.CANCEL,
                           "Descartar", Gtk.ResponseType.REJECT,
                           "Guardar", Gtk.ResponseType.ACCEPT)
        dialog.set_default_response(Gtk.ResponseType.CANCEL)
        self.confirmation = dialog
        dialog.connect("response", self._navigation_response, diagram)
        dialog.connect("close-request", self._confirmation_closed)
        keys = Gtk.EventControllerKey.new()
        keys.connect("key-pressed", self._confirmation_key_pressed)
        dialog.add_controller(keys)
        dialog.present()
        return False

    def _confirmation_closed(self, dialog):
        dialog.response(Gtk.ResponseType.CANCEL)
        return True

    def _confirmation_key_pressed(self, _controller, keyval, _keycode, _state):
        if keyval == Gdk.KEY_Escape:
            if self.confirmation:
                self.confirmation.response(Gtk.ResponseType.CANCEL)
            return True
        return False

    def _navigation_response(self, dialog, response, diagram):
        if self.confirmation is not dialog:
            return
        self.confirmation = None
        dialog.destroy()
        if response in (Gtk.ResponseType.ACCEPT, Gtk.ResponseType.REJECT):
            self._navigate(diagram, save=response == Gtk.ResponseType.ACCEPT)

    def _navigate(self, diagram, save=False):
        if not self._valid_diagram(diagram):
            return False
        if save and not self._save_fields():
            return False
        # Saving emits model events: recheck ownership before closing the editor.
        if not self._valid_diagram(diagram):
            return False
        parent = self.get_transient_for()
        self.cancel()
        try:
            self.event_manager.handle(DiagramOpened(diagram))
        except Exception:
            log.exception("No se pudo abrir el diagrama hijo")
            dialog = Gtk.MessageDialog(
                transient_for=parent, modal=True, message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.CLOSE, text="No se pudo abrir el diagrama.",
                secondary_text="Puedes intentar abrirlo desde el árbol de Gaphor.",
            )
            dialog.connect("response", lambda widget, _response: widget.destroy())
            dialog.present()
            return False
        return True

    def cancel(self):
        if not self.finished:
            self.finished = True
            if self.confirmation:
                dialog, self.confirmation = self.confirmation, None
                dialog.destroy()
            self.on_closed(self)
            self.destroy()

    def _close_request(self, _window):
        self.cancel()
        return True

    def _key_pressed(self, _controller, keyval, _keycode, _state):
        if keyval == Gdk.KEY_Escape:
            if self.confirmation:
                self.confirmation.response(Gtk.ResponseType.CANCEL)
                return True
            self.cancel()
            return True
        return False


class DescriptionEditor(Service, ActionProvider):
    def __init__(self, main_window, tools_menu, event_manager, element_factory, diagrams):
        self.main_window = main_window
        self.tools_menu = tools_menu
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.diagrams = diagrams
        self.focused = None
        self.editor = None
        self.compatible = version("gaphor") == SUPPORTED_VERSION
        self.style_runtime = None
        tools_menu.add_actions(self)
        event_manager.subscribe(self._diagram_selection)
        event_manager.subscribe(self._model_selection)
        event_manager.subscribe(self._reset_selection)
        if self.compatible:
            _services[event_manager] = self
            _install_hook()
            self.style_runtime = StyleRuntime(element_factory, event_manager)

    @event_handler(DiagramSelectionChanged)
    def _diagram_selection(self, event):
        self.focused = event.focused_item

    @event_handler(ModelSelectionChanged)
    def _model_selection(self, event):
        self.focused = event.focused_element

    @event_handler(ModelReady, CurrentDiagramChanged)
    def _reset_selection(self, _event):
        self.focused = None

    @action(name="edit-description", label="Propiedades…", shortcut="<Control><Alt>d")
    def edit_description(self):
        self.open_element(self.focused)

    def open_element(self, element):
        if not self.compatible:
            self._message("Este plugin requiere Gaphor 3.3.2. No se ha modificado el doble clic.")
            return
        subject = target_element(element)
        if subject is None:
            self._message("Selecciona un componente, artefacto u otro elemento UML. Los estereotipos no admiten esta extensión.")
            return
        if self.element_factory.lookup(subject.id) is not subject:
            self._message("El elemento seleccionado ya no pertenece a este modelo.")
            return
        if self.editor:
            self.editor.present()
            return
        try:
            self.editor = DocumentationWindow(
                self.main_window.window, subject, self.event_manager, self._editor_closed,
            )
        except DocumentationError as error:
            self._message(str(error))
            return
        self.editor.present()

    def _editor_closed(self, editor):
        if self.editor is editor:
            self.editor = None

    def _message(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.main_window.window, modal=True,
            message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.CLOSE,
            text="Propiedades", secondary_text=message,
        )
        dialog.connect("response", lambda widget, _response: widget.destroy())
        dialog.present()

    def shutdown(self):
        if self.editor:
            self.editor.cancel()
        self.event_manager.unsubscribe(self._diagram_selection)
        self.event_manager.unsubscribe(self._model_selection)
        self.event_manager.unsubscribe(self._reset_selection)
        _services.pop(self.event_manager, None)
        _remove_hook()
        if self.style_runtime:
            self.style_runtime.shutdown()
        self.tools_menu.remove_actions(self)


@PropertyPages.register(UML.Element)
class DescriptionPropertyPage(PropertyPageBase):
    order = 290

    def __init__(self, subject, event_manager):
        self.subject = target_element(subject)
        self.event_manager = event_manager
        self.watcher = None
        self.pending_refresh = 0
        self.preview = None

    def construct(self):
        if self.subject is None or self.event_manager not in _services:
            return None
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.add_css_class("propertypage")
        label = Gtk.Label(label="Descripción", xalign=0)
        label.add_css_class("title")
        box.append(label)
        self.preview = Gtk.Label(xalign=0, wrap=True, lines=3, max_width_chars=32, ellipsize=Pango.EllipsizeMode.END)
        box.append(self.preview)
        button = Gtk.Button(label="Propiedades…")
        button.connect("clicked", self._open)
        box.append(button)
        self.watcher = self.subject.watcher()
        self.watcher.watch("appliedStereotype.slot.value[LiteralString].value", self._changed)
        self._refresh()
        return box

    def _open(self, _button):
        if service := _services.get(self.event_manager):
            service.open_element(self.subject)

    def _changed(self, _event):
        if not self.pending_refresh:
            self.pending_refresh = GLib.idle_add(self._refresh)

    def _refresh(self):
        self.pending_refresh = 0
        if self.preview is not None:
            try:
                self.preview.set_text(read_description(self.subject) or "Sin descripción")
            except (DocumentationError, TypeError) as error:
                self.preview.set_text(str(error))
        return GLib.SOURCE_REMOVE

    def close(self):
        if self.watcher:
            self.watcher.unsubscribe_all()
            self.watcher = None
        if self.pending_refresh:
            GLib.source_remove(self.pending_refresh)
            self.pending_refresh = 0
        self.preview = None
