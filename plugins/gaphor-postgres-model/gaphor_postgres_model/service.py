"""Session-local commands, editor lifecycle and view refresh for PostgreSQL."""

import logging
from importlib.metadata import version

from gi.repository import Gio, GLib, Gtk
from gaphor import UML
from gaphor.abc import Service, ActionProvider
from gaphor.core import action, event_handler, Transaction
from gaphor.core.modeling import Presentation
from gaphor.core.modeling.event import ElementUpdated, ElementDeleted, ModelReady, ModelFlushed
from gaphor.core.modeling.event import AttributeUpdated
from gaphor.diagram.event import DiagramOpened, DiagramItemPlaced, DiagramSelectionChanged
from gaphor.diagram.propertypages import PropertyPages, PropertyPageBase
from gaphor.event import Notification
from gaphor.ui.event import ModelSelectionChanged, CurrentDiagramChanged

from . import SUPPORTED_GAPHOR
from .model import PGDatabase, PGSchema, PGTable, PGForeignKey, PGDiagram, MODEL_TYPES, database, rules, deletion_dependencies
from .operations import create_database, snapshot, new_fk, validate_edit
from .diagram import PGTableItem, PGForeignKeyItem, drop_fk
from .editor import TableEditor, label, button
from .validation import ModelError

log = logging.getLogger(__name__)
_services = {}
_original_clipboard_paste = None


async def _paste_with_relational_errors(clipboard, view, paster):
    try:
        return await _original_clipboard_paste(clipboard, view, paster)
    except ModelError as error:
        clipboard.event_manager.handle(Notification(str(error)))


def install_paste_guard():
    global _original_clipboard_paste
    from gaphor.ui.clipboard import Clipboard
    if _original_clipboard_paste is None:
        _original_clipboard_paste = Clipboard._paste
        Clipboard._paste = _paste_with_relational_errors


def remove_paste_guard():
    global _original_clipboard_paste
    from gaphor.ui.clipboard import Clipboard
    if not _services and _original_clipboard_paste is not None:
        if Clipboard._paste is _paste_with_relational_errors:
            Clipboard._paste = _original_clipboard_paste
        _original_clipboard_paste = None


def selected_table(element):
    if isinstance(element, Presentation):
        element = element.subject
    seen = set()
    while element is not None and id(element) not in seen:
        if isinstance(element, PGTable):
            return element
        seen.add(id(element))
        element = getattr(element, "owner", None)
    return None


class PostgresService(Service, ActionProvider):
    def __init__(self, main_window, tools_menu, event_manager, element_factory, diagrams):
        self.main_window, self.tools_menu, self.events = main_window, tools_menu, event_manager
        self.model, self.diagrams = element_factory, diagrams
        self.alive, self.window, self.focused, self.refresh_source = True, None, None, 0
        self.sources = set()
        self.compatible = version("gaphor") == SUPPORTED_GAPHOR
        _services[event_manager] = self
        install_paste_guard()
        if not hasattr(tools_menu, "exotic_custom_tools_menu"):
            tools_menu.exotic_custom_tools_menu = Gio.Menu.new()
            item = Gio.MenuItem.new_submenu("Custom tools", tools_menu.exotic_custom_tools_menu)
            item.set_attribute_value("x-exotic-custom-tools", GLib.Variant.new_boolean(True))
            tools_menu.menu.append_item(item)
        self.menu = Gio.Menu.new()
        self.menu.append("Nuevo diagrama relacional…", "win.pg-new-diagram")
        self.menu.append("Editar tabla…", "win.pg-edit-table")
        self.menu.append("Validar base de datos", "win.pg-validate")
        item = Gio.MenuItem.new_submenu("Modelo relacional", self.menu)
        item.set_attribute_value("x-exotic-postgres", GLib.Variant.new_boolean(True))
        tools_menu.exotic_custom_tools_menu.append_item(item)
        self.handlers = (self._selection, self._model_selection, self._diagram_changed,
                         self._placed, self._updated, self._reset)
        for handler in self.handlers:
            self.events.subscribe(handler)

    def notify(self, message):
        self.events.handle(Notification(message))

    @event_handler(ModelSelectionChanged)
    def _model_selection(self, event):
        self.focused = event.focused_element

    @event_handler(DiagramSelectionChanged)
    def _selection(self, event):
        self.focused = event.focused_item or getattr(event.diagram_view, "model", None)

    @event_handler(CurrentDiagramChanged)
    def _diagram_changed(self, event):
        self.focused = event.diagram

    @action(name="pg-new-diagram", label="Nuevo diagrama relacional…")
    def new_diagram(self):
        if not self._ready():
            return
        selected = self.focused.subject if isinstance(self.focused, Presentation) else self.focused
        root = database(selected)
        with Transaction(self.events):
            if root:
                diagram = self.model.create(PGDiagram)
                diagram.element, diagram.name = root, "Diagrama relacional"
            else:
                parent = selected if isinstance(selected, UML.Package) else None
                _, _, diagram = create_database(self.model, self.events, parent=parent)
        self.events.handle(DiagramOpened(diagram))
        return diagram

    def _ready(self):
        if not self.alive or not self.compatible:
            self.notify("Modelo relacional requiere Gaphor 3.3.2.")
            return False
        return True

    @action(name="pg-edit-table", label="Editar tabla…")
    def edit_table(self):
        self.open_table(selected_table(self.focused))

    def open_table(self, table, pending_fk=None, diagram=None):
        if not self._ready():
            return
        if not isinstance(table, PGTable) or self.model.lookup(table.id) is not table:
            self.notify("Selecciona una tabla PostgreSQL o una de sus columnas/restricciones.")
            return
        if self.window:
            self.window.present()
            if pending_fk:
                self.notify("Termina la edición actual antes de crear otra relación.")
            return
        active = diagram or self.diagrams.get_current_diagram()
        self.window = TableEditor(self.main_window.window, table, self.events, self._closed,
                                  after_save=lambda value: self._after_save(value, active), notify=self.notify)
        self.window.present()
        if pending_fk:
            self.window.tabs.set_current_page(1)
            self.window.lists["foreign_keys"].edit(pending_fk, is_new=True)
        return self.window

    def _closed(self, window):
        if self.window is window:
            self.window = None

    def _after_save(self, table, diagram):
        if diagram and self.model.lookup(diagram.id) is diagram:
            for fk in rules(table, PGForeignKey):
                if not any(p.diagram is diagram for p in fk.presentation):
                    drop_fk(fk, diagram, 0, 0)
        self.refresh()

    @event_handler(DiagramItemPlaced)
    def _placed(self, event):
        item = event.item
        if not isinstance(item, PGForeignKeyItem) or item.subject is not None:
            return
        diagram = item.diagram
        head = diagram.connections.get_connection(item.head)
        tail = diagram.connections.get_connection(item.tail)
        target = head.connected.subject if head else None
        source = tail.connected.subject if tail else None
        # Runs within the placement gesture transaction, so the preview never
        # becomes a saved model relation or a separately undoable incomplete FK.
        item.unlink()
        if not isinstance(source, PGTable) or not isinstance(target, PGTable) or database(source) is not database(target):
            self.notify("Conecta una tabla de origen con una tabla destino de la misma base de datos.")
            return
        draft = new_fk(target.id)
        from .operations import unique_name
        draft["name"] = unique_name(f"fk_{source.name}_{target.name}"[:55], rules(source))
        source_id = 0
        def open_pending():
            self.sources.discard(source_id)
            if self.alive and self.model.lookup(source.id) is source and self.model.lookup(target.id) is target:
                self.open_table(source, draft, diagram)
            return GLib.SOURCE_REMOVE
        source_id = GLib.idle_add(open_pending)
        self.sources.add(source_id)

    @event_handler(ElementUpdated, ElementDeleted)
    def _updated(self, event):
        if not isinstance(event.element, MODEL_TYPES):
            return
        # Rebuild shapes before the native transaction's layout/undo commit.
        # No geometry is changed here; Gaphor's sanitizer handles that once.
        self.refresh()
        if (isinstance(event, AttributeUpdated) and event.property.name == "name"
                and event.old_value and event.new_value and event.old_value != event.new_value
                and self.window is None):
            self.notify("Nombre modificado: las referencias estructuradas se conservan. Revisa las expresiones SQL textuales y usa Validar base de datos.")

    def refresh(self):
        if self.refresh_source:
            GLib.source_remove(self.refresh_source)
            self.refresh_source = 0
        if not self.alive:
            return GLib.SOURCE_REMOVE
        for diagram in self.model.select(UML.Diagram):
            changed = []
            for item in diagram.get_all_items():
                if isinstance(item, PGTableItem):
                    item.update_shapes()
                    changed.append(item)
                elif isinstance(item, PGForeignKeyItem):
                    item.request_update()
                    changed.append(item)
            if changed:
                # Gaphor's diagram-layout service resolves sizes within the
                # native transaction. Idle callbacks must not change geometry.
                for item in changed:
                    diagram.request_update(item)
        return GLib.SOURCE_REMOVE

    @action(name="pg-validate", label="Validar base de datos")
    def validate_database(self):
        selected = self.focused.subject if isinstance(self.focused, Presentation) else self.focused
        root = database(selected)
        if root is None:
            current = self.diagrams.get_current_diagram()
            root = database(current.element) if current else None
        if root is None:
            self.notify("Selecciona una base de datos PostgreSQL.")
            return
        problems = []
        for table in self.model.select(PGTable):
            if database(table) is root:
                try:
                    problems.extend(validate_edit(table, snapshot(table)))
                except ModelError as error:
                    problems.append(f"{table.name}: {error}")
        self.notify("\n".join(dict.fromkeys(problems)) if problems else
                    "Estructura relacional válida. Las expresiones SQL no se han validado contra PostgreSQL.")
        return problems

    @event_handler(ModelReady, ModelFlushed)
    def _reset(self, event):
        self.focused = None
        if self.window:
            self.window.cancel()
        self.refresh()

    def shutdown(self):
        if not self.alive:
            return
        self.alive = False
        if self.window:
            self.window.cancel()
        if self.refresh_source:
            GLib.source_remove(self.refresh_source)
            self.refresh_source = 0
        for source in self.sources:
            GLib.source_remove(source)
        self.sources.clear()
        for handler in self.handlers:
            self.events.unsubscribe(handler)
        _services.pop(self.events, None)
        remove_paste_guard()
        menu = self.tools_menu.exotic_custom_tools_menu
        for index in reversed(range(menu.get_n_items())):
            if menu.get_item_attribute_value(index, "x-exotic-postgres", None):
                menu.remove(index)


@PropertyPages.register(UML.Element)
class RelationalPropertyPage(PropertyPageBase):
    order = 275

    def __init__(self, subject, event_manager):
        self.subject, self.events = subject, event_manager

    def construct(self):
        table = selected_table(self.subject)
        service = _services.get(self.events)
        if not table or not service:
            return None
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.add_css_class("propertypage")
        box.append(label("PostgreSQL"))
        box.append(button("Editar tabla…", lambda: service.open_table(table)))
        dependencies = deletion_dependencies(self.subject)
        if dependencies:
            box.append(label("Para eliminar, resuelve primero: " + ", ".join(r.name for r in dependencies)))
        return box
