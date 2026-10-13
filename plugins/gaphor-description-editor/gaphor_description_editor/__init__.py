"""Gaphor 3.3.2 session plugin: independent Description and Note editors."""

import logging
from importlib.metadata import version

from gi.repository import Gdk, GLib, Gtk, Pango

from gaphor import UML
from gaphor.abc import ActionProvider, Service
from gaphor.core import action, event_handler
from gaphor.core.modeling.event import ModelReady
from gaphor.diagram.event import DiagramSelectionChanged
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages
from gaphor.diagram.tools import textedit
from gaphor.ui.event import CurrentDiagramChanged, ModelSelectionChanged

from .model import DocumentationError, read_description, save_documentation, target_element

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
            title=f"Descripción — {getattr(subject, 'name', '') or type(subject).__name__}",
            transient_for=parent,
            modal=True,
            resizable=True,
            default_width=900,
            default_height=650,
        )
        self.subject = subject
        self.event_manager = event_manager
        self.on_closed = on_closed
        self.initial = (read_description(subject), subject.note or "")
        self.finished = False

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
        layout.append(self.paned)
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
    def _field(title, text):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        label = Gtk.Label(label=title, xalign=0)
        label.add_css_class("heading")
        box.append(label)
        buffer = Gtk.TextBuffer()
        buffer.set_text(text)
        view = Gtk.TextView(
            buffer=buffer, wrap_mode=Gtk.WrapMode.WORD_CHAR,
            top_margin=12, bottom_margin=12, left_margin=12, right_margin=12,
        )
        label.set_mnemonic_widget(view)
        scroll = Gtk.ScrolledWindow(vexpand=True, min_content_height=100)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(view)
        frame = Gtk.Frame(child=scroll)
        box.append(frame)
        return box, buffer, view

    def save(self):
        try:
            save_documentation(
                self.subject, _buffer_text(self.description_buffer),
                _buffer_text(self.note_buffer), self.event_manager, expected=self.initial,
            )
        except DocumentationError as error:
            self.error.set_text(str(error))
            self.error.set_visible(True)
            return False
        except Exception:
            log.exception("No se pudo guardar la documentación")
            self.error.set_text("No se pudo guardar. Conserva tu texto y consulta el registro de Gaphor.")
            self.error.set_visible(True)
            return False
        self.cancel()
        return True

    def cancel(self):
        if not self.finished:
            self.finished = True
            self.on_closed(self)
            self.destroy()

    def _close_request(self, _window):
        self.cancel()
        return True

    def _key_pressed(self, _controller, keyval, _keycode, _state):
        if keyval == Gdk.KEY_Escape:
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
        tools_menu.add_actions(self)
        event_manager.subscribe(self._diagram_selection)
        event_manager.subscribe(self._model_selection)
        event_manager.subscribe(self._reset_selection)
        if self.compatible:
            _services[event_manager] = self
            _install_hook()

    @event_handler(DiagramSelectionChanged)
    def _diagram_selection(self, event):
        self.focused = event.focused_item

    @event_handler(ModelSelectionChanged)
    def _model_selection(self, event):
        self.focused = event.focused_element

    @event_handler(ModelReady, CurrentDiagramChanged)
    def _reset_selection(self, _event):
        self.focused = None

    @action(name="edit-description", label="Editar descripción", shortcut="<Control><Alt>d")
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
            text="Editor de descripción", secondary_text=message,
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
        button = Gtk.Button(label="Editar descripción…")
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
