"""Detached property drafts; only Save changes the native Gaphor model."""

import logging

from gi.repository import Gdk, Gtk
from gaphor.core import Transaction

from . import model
from .operations import snapshot, update_element
from .validation import ModelError

log = logging.getLogger(__name__)


def label(text):
    return Gtk.Label(label=text, xalign=0, wrap=True)


def button(text, callback):
    result = Gtk.Button(label=text)
    result.connect("clicked", lambda _button: callback())
    return result


def choice(values, selected=""):
    result = Gtk.ComboBoxText(hexpand=True)
    for key, title in values:
        result.append(str(key), title)
    result.set_active_id(str(selected or ""))
    return result


def text_area(text):
    result = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD_CHAR)
    result.get_buffer().set_text(text or "")
    scroll = Gtk.ScrolledWindow(min_content_height=90, hexpand=True)
    scroll.set_child(result)
    return scroll, result


def read_text(widget):
    buffer = widget.get_buffer()
    return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)


EVENT_OPTIONS = (
    ("START|NONE|CATCH", "Inicio — sin disparador"),
    ("START|MESSAGE|CATCH", "Inicio — recepción de mensaje"),
    ("START|TIMER|CATCH", "Inicio — temporizador"),
    ("INTERMEDIATE|NONE|THROW", "Intermedio — lanzamiento sin disparador"),
    ("INTERMEDIATE|MESSAGE|CATCH", "Intermedio — recepción de mensaje"),
    ("INTERMEDIATE|MESSAGE|THROW", "Intermedio — envío de mensaje"),
    ("INTERMEDIATE|TIMER|CATCH", "Intermedio — temporizador"),
    ("END|NONE|THROW", "Fin — sin resultado específico"),
    ("END|MESSAGE|THROW", "Fin — envío de mensaje"),
)


class BPMNEditor(Gtk.Window):
    """A single-element editor with optimistic concurrency and atomic Save."""

    def __init__(self, parent, subject, events, on_close=lambda _window: None, after_save=None):
        super().__init__(title="Propiedades BPMN", transient_for=parent, modal=True,
                         default_width=570, default_height=620, resizable=True)
        self.subject, self.events = subject, events
        self.on_close, self.after_save = on_close, after_save
        self.expected = snapshot(subject)
        self.finished = False
        self.controls = {}
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        for side in ("top", "bottom", "start", "end"):
            getattr(outer, f"set_margin_{side}")(14)
        scroll = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
        self.form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scroll.set_child(self.form)
        outer.append(scroll)
        self.name = Gtk.Entry(text=subject.name or "", hexpand=True)
        self.field("Nombre", self.name)
        container = getattr(subject, "container", None)
        if container:
            self.form.append(label("Contenedor: " + (container.name or type(container).__name__)))
        doc_scroll, self.documentation = text_area(subject.documentation)
        self.field("Documentación BPMN", doc_scroll)
        self._specific_fields()
        self.error = label("")
        self.error.add_css_class("error")
        outer.append(self.error)
        actions = Gtk.Box(spacing=8, halign=Gtk.Align.END)
        actions.append(button("Cancelar", self.cancel))
        self.save_button = button("Guardar", self.save)
        self.save_button.add_css_class("suggested-action")
        actions.append(self.save_button)
        outer.append(actions)
        self.set_child(outer)
        self.connect("close-request", self._close_request)
        controller = Gtk.EventControllerKey()
        controller.connect("key-pressed", self._key_pressed)
        self.add_controller(controller)

    def field(self, title, widget):
        self.form.append(label(title))
        self.form.append(widget)
        return widget

    def _specific_fields(self):
        subject = self.subject
        if isinstance(subject, model.BPMNEvent):
            key = "|".join((subject.eventKind, subject.eventDefinition, subject.eventDirection))
            self.controls["event"] = self.field("Tipo de evento", choice(EVENT_OPTIONS, key))
        if isinstance(subject, model.BPMNGateway):
            self.controls["gatewayKind"] = self.field("Tipo de compuerta", choice(
                (("EXCLUSIVE", "Exclusiva (XOR)"), ("PARALLEL", "Paralela (AND)")), subject.gatewayKind))
        if isinstance(subject, model.BPMNFlowNode):
            process = model.process(subject)
            lanes = [lane for lane in subject.model.select(model.BPMNLane) if model.process(lane) is process]
            lane_values = [("", "Sin carril"), *((lane.id, lane.name or "Carril sin nombre") for lane in lanes)]
            self.controls["lane"] = self.field("Carril del mismo proceso", choice(lane_values, subject.lane.id if subject.lane else ""))
        if isinstance(subject, model.BPMNParticipant):
            closed = Gtk.CheckButton(label="Participante cerrado (sin proceso interno)")
            closed.set_active(subject.isClosed)
            self.controls["isClosed"] = self.field("Representación del participante", closed)
            self.form.append(label("Para cerrar un participante, su proceso debe estar vacío. Usa el pool abierto para representar su trabajo interno."))
        if isinstance(subject, model.BPMNSequenceFlow):
            self.controls["flowKind"] = self.field("Tipo de flujo de secuencia", choice(
                (("NORMAL", "Ordinario"), ("CONDITIONAL", "Condicional"), ("DEFAULT", "Predeterminado")), subject.flowKind))
            scroll, field = text_area(subject.conditionExpression)
            self.field("Condición descriptiva (no se evalúa)", scroll)
            self.controls["conditionExpression"] = field
        if isinstance(subject, model.BPMNTextAnnotation):
            scroll, field = text_area(subject.text)
            self.field("Texto de la anotación", scroll)
            self.controls["text"] = field
        if isinstance(subject, (model.BPMNSequenceFlow, model.BPMNMessageFlow, model.BPMNAssociation)):
            self.form.append(label("Para cambiar los extremos, reconecta la línea en el diagrama. Las referencias se conservan al renombrar elementos."))
        if isinstance(subject, model.BPMNSubProcess):
            self.form.append(label("Subproceso integrado colapsado. Esta versión no ofrece edición de su descomposición interna."))

    def changes(self):
        result = {"name": self.name.get_text(), "documentation": read_text(self.documentation)}
        for key, widget in self.controls.items():
            if key == "event":
                selected = widget.get_active_id()
                if not selected:
                    raise ModelError("Selecciona una combinación de evento soportada.")
                result.update(zip(("eventKind", "eventDefinition", "eventDirection"), selected.split("|")))
            elif isinstance(widget, Gtk.ComboBoxText):
                result[key] = widget.get_active_id() or ""
            elif isinstance(widget, Gtk.CheckButton):
                result[key] = widget.get_active()
            elif isinstance(widget, Gtk.TextView):
                result[key] = read_text(widget)
        return result

    def save(self):
        if self.finished:
            return False
        try:
            if self.subject.model.lookup(self.subject.id) is not self.subject:
                raise ModelError("El elemento fue eliminado. Cierra este editor.")
            with Transaction(self.events):
                update_element(self.subject, self.changes(), self.events, expected=self.expected)
                if self.after_save:
                    self.after_save(self.subject)
        except (ModelError, ValueError) as error:
            self.error.set_text(str(error))
            return False
        except Exception:
            log.exception("No se pudieron guardar las propiedades BPMN")
            self.error.set_text("No se pudieron guardar los cambios; el modelo se ha restaurado. Consulta el registro de Gaphor.")
            return False
        self._finish()
        return True

    def cancel(self):
        if not self.finished:
            self._finish()

    def _finish(self):
        self.finished = True
        self.on_close(self)
        self.destroy()

    def _close_request(self, _window):
        self.cancel()
        return True

    def _key_pressed(self, _controller, keyval, _keycode, _state):
        if keyval == Gdk.KEY_Escape:
            self.cancel()
            return True
        return False
