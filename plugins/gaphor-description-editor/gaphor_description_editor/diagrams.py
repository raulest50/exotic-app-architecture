"""Read-only navigation through an element's native, directly owned diagrams."""

from collections import Counter
import re

from gi.repository import Gdk, Gtk, Pango
from gaphor import UML


def diagram_name(diagram):
    return diagram.name or "Sin nombre"


def diagram_type(diagram):
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", type(diagram).__name__)


class DiagramList(Gtk.Box):
    def __init__(self, subject, on_open):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.subject = subject
        self.model = subject.model
        self.on_open = on_open
        self.append(Gtk.Label(label="Diagramas que pertenecen directamente a este elemento.", xalign=0))
        self.listbox = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE,
                                   activate_on_single_click=False)
        self.empty = Gtk.Label(label="Este elemento no tiene diagramas hijos", wrap=True,
                               margin_top=24, margin_bottom=24)
        self.listbox.set_placeholder(self.empty)
        self.listbox.connect("row-selected", self._selected)
        self.listbox.connect("row-activated", lambda _list, row: self.on_open(row.diagram))
        self.keys = Gtk.EventControllerKey.new()
        self.keys.connect("key-pressed", self._key_pressed)
        self.listbox.add_controller(self.keys)
        scroll = Gtk.ScrolledWindow(vexpand=True, min_content_height=180)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(self.listbox)
        self.append(Gtk.Frame(child=scroll))
        self.open_button = Gtk.Button(label="Abrir", halign=Gtk.Align.END, sensitive=False)
        self.open_button.connect("clicked", lambda _button: self.open_selected())
        self.append(self.open_button)
        self.refresh()

    def refresh(self):
        selected = self.listbox.get_selected_row()
        selected_id = selected.diagram.id if selected else None
        while row := self.listbox.get_row_at_index(0):
            self.listbox.remove(row)
        diagrams = []
        if self.model.lookup(self.subject.id) is self.subject:
            diagrams = sorted(
                (d for d in self.subject.ownedDiagram
                 if isinstance(d, UML.Diagram) and d.element is self.subject
                 and self.model.lookup(d.id) is d),
                key=lambda d: (diagram_name(d).casefold(), diagram_type(d), d.id),
            )
        names = Counter(diagram_name(d).casefold() for d in diagrams)
        for diagram in diagrams:
            name = diagram_name(diagram)
            title = name
            if names[name.casefold()] > 1:
                others = [d.id for d in diagrams if d is not diagram
                          and diagram_name(d).casefold() == name.casefold()]
                length = 8
                while length < len(diagram.id) and any(
                    other[:length] == diagram.id[:length] for other in others
                ):
                    length += 1
                title = f"{name} · {diagram.id[:length]}"
            row = Gtk.ListBoxRow()
            row.diagram = diagram
            content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4,
                              margin_top=10, margin_bottom=10, margin_start=12, margin_end=12)
            content.append(Gtk.Label(label=title, xalign=0, ellipsize=Pango.EllipsizeMode.END,
                                     tooltip_text=f"{name}\n{diagram.id}"))
            kind = Gtk.Label(label=diagram_type(diagram), xalign=0)
            kind.add_css_class("dim-label")
            content.append(kind)
            row.set_child(content)
            self.listbox.append(row)
            if diagram.id == selected_id:
                self.listbox.select_row(row)
        self.open_button.set_sensitive(self.listbox.get_selected_row() is not None)

    def _selected(self, _listbox, row):
        self.open_button.set_sensitive(row is not None)

    def open_selected(self):
        if row := self.listbox.get_selected_row():
            self.on_open(row.diagram)

    def _key_pressed(self, _controller, keyval, _keycode, _state):
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self.open_selected()
            return True
        return False
