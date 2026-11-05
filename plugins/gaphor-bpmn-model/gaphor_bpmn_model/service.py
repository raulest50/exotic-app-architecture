"""Session-local BPMN commands, property entry points and validation report."""

from importlib.metadata import version

from gi.repository import Gio, GLib, Gtk
from gaphor import UML
from gaphor.abc import ActionProvider, Service
from gaphor.core import Transaction, action, event_handler
from gaphor.core.modeling import Presentation
from gaphor.core.modeling.event import ElementDeleted, ElementUpdated, ModelFlushed, ModelReady
from gaphor.diagram.event import DiagramItemPlaced, DiagramOpened, DiagramSelectionChanged
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages
from gaphor.event import Notification
from gaphor.ui.event import CurrentDiagramChanged, ModelSelectionChanged

from . import SUPPORTED_GAPHOR, model
from .editor import BPMNEditor, button, label
from .operations import create_collaboration, delete_participant as delete_participant_model
from .validation import validate

_services = {}


def selected_subject(value):
    return value.subject if isinstance(value, Presentation) else value


def selected_collaboration(value):
    value = selected_subject(value)
    return model.collaboration(value) if value is not None else None


class BPMNService(Service, ActionProvider):
    def __init__(self, main_window, tools_menu, event_manager, element_factory, diagrams):
        self.main_window, self.tools_menu, self.events = main_window, tools_menu, event_manager
        self.model, self.diagrams = element_factory, diagrams
        self.alive = True
        self.window = self.report = self.focused = self.delete_window = None
        self.compatible = version("gaphor") == SUPPORTED_GAPHOR
        _services[self.events] = self
        if not hasattr(tools_menu, "exotic_custom_tools_menu"):
            tools_menu.exotic_custom_tools_menu = Gio.Menu.new()
            item = Gio.MenuItem.new_submenu("Custom tools", tools_menu.exotic_custom_tools_menu)
            item.set_attribute_value("x-exotic-custom-tools", GLib.Variant.new_boolean(True))
            tools_menu.menu.append_item(item)
        self.menu = Gio.Menu.new()
        self.menu.append("Nuevo diagrama BPMN", "win.bpmn-new-diagram")
        self.menu.append("Editar propiedades BPMN…", "win.bpmn-edit")
        self.menu.append("Validar BPMN", "win.bpmn-validate")
        self.menu.append("Eliminar participante BPMN…", "win.bpmn-delete-participant")
        item = Gio.MenuItem.new_submenu("BPMN", self.menu)
        item.set_attribute_value("x-exotic-bpmn", GLib.Variant.new_boolean(True))
        tools_menu.exotic_custom_tools_menu.append_item(item)
        self.handlers = (self._selection, self._model_selection, self._diagram_changed,
                         self._placed, self._updated, self._reset)
        for handler in self.handlers:
            self.events.subscribe(handler)

    def notify(self, text):
        self.events.handle(Notification(text))

    def _ready(self):
        if not self.alive or not self.compatible:
            self.notify("BPMN requiere Gaphor 3.3.2.")
            return False
        return True

    @event_handler(ModelSelectionChanged)
    def _model_selection(self, event):
        self.focused = event.focused_element

    @event_handler(DiagramSelectionChanged)
    def _selection(self, event):
        self.focused = event.focused_item or getattr(event.diagram_view, "model", None)

    @event_handler(CurrentDiagramChanged)
    def _diagram_changed(self, event):
        self.focused = event.diagram

    @action(name="bpmn-new-diagram", label="Nuevo diagrama BPMN")
    def new_diagram(self):
        if not self._ready():
            return None
        root = selected_collaboration(self.focused)
        with Transaction(self.events):
            if root:
                diagram = self.model.create(model.BPMNDiagram)
                selected = selected_subject(self.focused)
                owner = selected.element if isinstance(selected, model.BPMNDiagram) else root.folder or root
                diagram.element, diagram.name = owner, "Diagrama BPMN"
                diagram.bpmnCollaboration = root
            else:
                selected = selected_subject(self.focused)
                folder = selected if isinstance(selected, UML.Package) else None
                _, diagram = create_collaboration(self.model, self.events, name="Colaboración",
                                                  folder=folder, diagram_owner=folder)
        self.focused = diagram
        self.events.handle(DiagramOpened(diagram))
        return diagram

    @action(name="bpmn-edit", label="Editar propiedades BPMN…")
    def edit(self):
        return self.open_editor(selected_subject(self.focused))

    def open_editor(self, subject):
        if not self._ready():
            return None
        if not isinstance(subject, model.BPMNElement) or self.model.lookup(subject.id) is not subject:
            self.notify("Selecciona un elemento BPMN en el diagrama o en el árbol.")
            return None
        if self.window:
            self.window.present()
            return self.window
        self.window = BPMNEditor(self.main_window.window, subject, self.events, self._editor_closed,
                                 after_save=lambda _subject: self.refresh())
        self.window.present()
        return self.window

    def _editor_closed(self, window):
        if self.window is window:
            self.window = None

    @action(name="bpmn-delete-participant", label="Eliminar participante BPMN…")
    def delete_participant(self):
        if not self._ready():
            return None
        subject = selected_subject(self.focused)
        if not isinstance(subject, model.BPMNParticipant) or self.model.lookup(subject.id) is not subject:
            self.notify("Selecciona el pool del participante que quieres eliminar.")
            return None
        if self.delete_window:
            self.delete_window.present()
            return self.delete_window
        window = Gtk.Window(title="Eliminar participante BPMN", transient_for=self.main_window.window,
                            modal=True, default_width=520, resizable=True)
        self.delete_window = window
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        for side in ("top", "bottom", "start", "end"):
            getattr(box, f"set_margin_{side}")(18)
        box.append(label(f"Se eliminarán «{subject.name or 'Participante'}», su proceso, carriles, nodos y flujos incidentes. La operación puede deshacerse."))
        error = label("")
        error.add_css_class("error")
        box.append(error)
        actions = Gtk.Box(spacing=8, halign=Gtk.Align.END)
        def close():
            if self.delete_window is window:
                self.delete_window = None
            window.destroy()
        def confirm():
            try:
                delete_participant_model(subject, self.events)
            except ValueError as problem:
                error.set_text(str(problem))
                return
            self.focused = None
            close()
        actions.append(button("Cancelar", close))
        remove = button("Eliminar participante", confirm)
        remove.add_css_class("destructive-action")
        actions.append(remove)
        box.append(actions)
        window.set_child(box)
        def request_close(_window):
            close()
            return True
        window.connect("close-request", request_close)
        window.present()
        return window

    @event_handler(DiagramItemPlaced)
    def _placed(self, event):
        from .diagram import BPMNAssociationItem, BPMNMessageFlowItem, BPMNSequenceFlowItem
        item = event.item
        error = getattr(item, "_bpmn_placement_error", "")
        if isinstance(item, (BPMNSequenceFlowItem, BPMNMessageFlowItem, BPMNAssociationItem)):
            subject = item.subject
            if not subject or not subject.sourceRef or not subject.targetRef:
                error = error or "Conecta ambos extremos del flujo a elementos BPMN compatibles."
        if not error:
            return
        subject = item.subject
        item.unlink()
        if subject and self.model.lookup(subject.id) is subject and not subject.presentation:
            subject.unlink()
        self.notify(error)

    @event_handler(ElementUpdated, ElementDeleted)
    def _updated(self, event):
        if not isinstance(event.element, model.BPMNElement):
            return
        if isinstance(event, ElementDeleted) and self.window and self.window.subject is event.element:
            self.window.cancel()
        self.refresh()

    def refresh(self):
        if not self.alive:
            return
        for diagram in self.model.select(UML.Diagram):
            for item in diagram.get_all_items():
                if type(item).__module__ != "gaphor_bpmn_model.diagram":
                    continue
                if callable(update := getattr(item, "update_shapes", None)):
                    update()
                item.request_update()

    @action(name="bpmn-validate", label="Validar BPMN")
    def validate_diagram(self):
        if not self._ready():
            return None
        root = selected_collaboration(self.focused)
        if root is None:
            root = selected_collaboration(self.diagrams.get_current_diagram())
        if root is None:
            self.notify("Abre o selecciona un diagrama BPMN.")
            return None
        diagnostics = validate(root, final=True)
        lines = ["Validación descriptiva del subconjunto BPMN soportado.",
                 "No comprueba ejecución, condiciones ni conformidad completa con BPMN.", ""]
        for diagnostic in diagnostics:
            element = self.model.lookup(diagnostic.element_id) if diagnostic.element_id else None
            title = getattr(element, "name", "") or diagnostic.element_id or "Modelo"
            lines.append(f"{diagnostic.severity} — {title}: {diagnostic.message} [{diagnostic.code}]")
        if not diagnostics:
            lines.append("Sin problemas detectados por las reglas implementadas.")
        self._show_report("\n".join(lines))
        return diagnostics

    def _show_report(self, text):
        if self.report:
            self.report.destroy()
        self.report = Gtk.Window(title="Validación BPMN", transient_for=self.main_window.window,
                                 default_width=720, default_height=470, resizable=True)
        scroll = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
        view = Gtk.TextView(editable=False, cursor_visible=False, wrap_mode=Gtk.WrapMode.WORD_CHAR)
        view.get_buffer().set_text(text)
        for side in ("top", "bottom", "start", "end"):
            getattr(view, f"set_margin_{side}")(12)
        scroll.set_child(view)
        self.report.set_child(scroll)
        self.report.present()

    @event_handler(ModelReady, ModelFlushed)
    def _reset(self, event):
        self.focused = None
        if self.window:
            self.window.cancel()
        if self.report:
            self.report.destroy()
            self.report = None
        if self.delete_window:
            self.delete_window.destroy()
            self.delete_window = None

    def shutdown(self):
        if not self.alive:
            return
        self.alive = False
        if self.window:
            self.window.cancel()
        if self.report:
            self.report.destroy()
            self.report = None
        if self.delete_window:
            self.delete_window.destroy()
            self.delete_window = None
        for handler in self.handlers:
            self.events.unsubscribe(handler)
        _services.pop(self.events, None)
        menu = self.tools_menu.exotic_custom_tools_menu
        for index in reversed(range(menu.get_n_items())):
            if menu.get_item_attribute_value(index, "x-exotic-bpmn", None):
                menu.remove(index)


@PropertyPages.register(model.BPMNElement)
class BPMNPropertyPage(PropertyPageBase):
    order = 280

    def __init__(self, subject, event_manager):
        self.subject, self.events = subject, event_manager

    def construct(self):
        service = _services.get(self.events)
        if not service:
            return None
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.add_css_class("propertypage")
        box.append(label("BPMN"))
        box.append(button("Editar propiedades BPMN…", lambda: service.open_editor(self.subject)))
        box.append(button("Validar BPMN", service.validate_diagram))
        if model.deletion_dependencies(self.subject):
            box.append(label("Para borrar este elemento, resuelve primero sus referencias. Para retirar un pool con su proceso, usa Eliminar participante BPMN… en el menú BPMN."))
        return box
