"""Detached GTK drafts: table editor and small editors for each relational row."""

from copy import deepcopy
import logging
from gi.repository import Gdk, Gtk, Pango
from gaphor.core import Transaction
from .model import PGTable, database, qualified_name
from .operations import (snapshot, save_table, new_column, new_key, new_fk, new_check,
                         new_index, token)
from .validation import ModelError, ACTIONS, METHODS, IDENTITIES, ORDERS, TYPES

log = logging.getLogger(__name__)


def label(text):
    return Gtk.Label(label=text, xalign=0, wrap=True)


def button(text, callback):
    b = Gtk.Button(label=text)
    b.connect("clicked", lambda _b: callback())
    return b


def entry(value=""):
    return Gtk.Entry(text=value or "", hexpand=True)


def choice(values, selected=None):
    """Stable IDs in combo boxes, never parse labels to recover model references."""
    combo = Gtk.ComboBoxText(hexpand=True)
    for key, name in values:
        combo.append(key, name)
    combo.set_active_id(selected or "")
    return combo


def enum(values, selected):
    return choice([(v, v) for v in values], selected)


def text_area(value):
    view = Gtk.TextView(monospace=True, wrap_mode=Gtk.WrapMode.WORD_CHAR)
    view.get_buffer().set_text(value)
    scroll = Gtk.ScrolledWindow(min_content_height=85, hexpand=True)
    scroll.set_child(view)
    def read():
        buf = view.get_buffer()
        return buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)
    return scroll, read


class Form(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        for side in ("top", "bottom", "start", "end"):
            getattr(self, f"set_margin_{side}")(14)

    def field(self, title, widget):
        self.append(label(title))
        self.append(widget)
        return widget


class OrderedColumns(Gtk.Box):
    def __init__(self, available, selected):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.available, self.selected = available, list(selected)
        self.rows = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.append(self.rows)
        self.selector = choice(available)
        line = Gtk.Box(spacing=6)
        line.append(self.selector)
        line.append(button("Añadir columna", self.add))
        self.append(line)
        self.refresh()

    def add(self):
        cid = self.selector.get_active_id()
        if cid and cid not in self.selected:
            self.selected.append(cid)
            self.refresh()

    def refresh(self):
        while child := self.rows.get_first_child():
            self.rows.remove(child)
        names = dict(self.available)
        for i, cid in enumerate(self.selected):
            row = Gtk.Box(spacing=4)
            name = label(names.get(cid, "(columna eliminada)"))
            name.set_hexpand(True)
            row.append(name)
            row.append(button("↑", lambda i=i: self.move(i, -1)))
            row.append(button("↓", lambda i=i: self.move(i, 1)))
            row.append(button("Quitar", lambda i=i: self.remove_at(i)))
            self.rows.append(row)

    def move(self, index, delta):
        other = index + delta
        if 0 <= other < len(self.selected):
            self.selected[index], self.selected[other] = self.selected[other], self.selected[index]
            self.refresh()

    def remove_at(self, index):
        self.selected.pop(index)
        self.refresh()


class Rows(Gtk.Box):
    """Ordered expression/column rows or local-to-remote FK mappings."""
    def __init__(self, records, local, remote=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.local, self.remote, self.controls = local, remote, []
        self.body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.append(self.body)
        self.append(button("Añadir correspondencia" if remote is not None else "Añadir campo", self.add))
        for rec in records:
            self.add(rec)

    def add(self, rec=None):
        rec = deepcopy(rec) if rec else dict(id=token(), local="", remote="", column="", expression="", order="DEFAULT")
        row = Gtk.Box(spacing=6)
        first = choice([("", "— Columna —"), *self.local], rec.get("local", "") if self.remote is not None else rec.get("column", ""))
        second = choice(self.remote, rec.get("remote", "")) if self.remote is not None else entry(rec.get("expression", ""))
        row.append(first)
        row.append(second)
        order = None
        if self.remote is None:
            second.set_placeholder_text("O expresión SQL (sin columna)")
            order = enum(ORDERS, rec.get("order", "DEFAULT"))
            row.append(order)
        values = (rec["id"], row, first, second, order)
        row.append(button("↑", lambda: self.move(values, -1)))
        row.append(button("↓", lambda: self.move(values, 1)))
        row.append(button("Quitar", lambda: self.remove_row(values)))
        self.controls.append(values)
        self.body.append(row)

    def remove_row(self, values):
        self.controls.remove(values)
        self.body.remove(values[1])

    def move(self, values, delta):
        pos = self.controls.index(values)
        other = pos + delta
        if 0 <= other < len(self.controls):
            self.controls[pos], self.controls[other] = self.controls[other], self.controls[pos]
            previous = None
            for _, row, *_ in self.controls:
                self.body.reorder_child_after(row, previous)
                previous = row

    def read(self):
        if self.remote is not None:
            return [dict(id=rid, local=a.get_active_id() or "", remote=b.get_active_id() or "")
                    for rid, _, a, b, _ in self.controls]
        return [dict(id=rid, column=a.get_active_id() or "", expression=b.get_text(), order=o.get_active_id())
                for rid, _, a, b, o in self.controls]


class Modal(Gtk.Window):
    def __init__(self, parent, title, width=850, height=620):
        super().__init__(title=title, transient_for=parent, modal=True, resizable=True,
                         default_width=width, default_height=height)
        self.finished = False
        self.header = Gtk.HeaderBar()
        self.header.pack_start(button("Cancelar", self.cancel))
        self.save_button = button("Guardar", self.save)
        self.save_button.add_css_class("suggested-action")
        self.header.pack_end(self.save_button)
        self.set_titlebar(self.header)
        self.layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.error = label("")
        self.error.add_css_class("error")
        self.layout.append(self.error)
        self.set_child(self.layout)
        self.connect("close-request", self._close)
        keys = Gtk.EventControllerKey.new()
        keys.connect("key-pressed", self._key)
        self.add_controller(keys)

    def _key(self, _controller, key, _code, _state):
        if key == Gdk.KEY_Escape:
            self.cancel()
            return True
        return False

    def _close(self, _window):
        self.cancel()
        return True

    def cancel(self):
        self.finished = True
        self.destroy()


class RecordEditor(Modal):
    def __init__(self, parent, kind, record, done):
        super().__init__(parent, {"columns": "Columna", "keys": "Clave", "foreign_keys": "Clave foránea",
                                 "checks": "Restricción CHECK", "indexes": "Índice"}[kind])
        self.parent_editor, self.kind, self.record, self.done = parent, kind, deepcopy(record), done
        self.form = form = Form()
        scroll = Gtk.ScrolledWindow(vexpand=True)
        scroll.set_child(form)
        self.layout.prepend(scroll)
        self.name = form.field("Nombre", entry(record["name"]))
        self.local = [(c["id"], c["name"] or "(sin nombre)") for c in parent.draft["columns"]]
        if kind == "columns":
            self.type = Gtk.ComboBoxText.new_with_entry()
            for text in TYPES:
                self.type.append_text(text)
            self.type.get_child().set_text(record["type"])
            form.field("Tipo PostgreSQL (también admite texto libre)", self.type)
            self.nullable = Gtk.CheckButton(label="Permite NULL", active=record["nullable"])
            form.append(self.nullable)
            self.default, self.read_default = text_area(record["default"])
            form.field("DEFAULT — expresión SQL", self.default)
            self.identity = form.field("Identidad", enum(IDENTITIES, record["identity"]))
        elif kind == "keys":
            self.key_kind = form.field("Tipo", enum(("PRIMARY", "UNIQUE"), record["kind"]))
            self.columns = form.field("Columnas (orden de la clave)", OrderedColumns(self.local, record["columns"]))
            self.nulls = Gtk.CheckButton(label="NULLS NOT DISTINCT (UNIQUE)", active=record["nulls_not_distinct"])
            form.append(self.nulls)
        elif kind == "foreign_keys":
            root = database(parent.table)
            self.targets = {t.id: t for t in parent.table.model.select(PGTable) if database(t) is root}
            values = [(t.id, qualified_name(t)) for t in sorted(self.targets.values(), key=qualified_name)]
            self.target = form.field("Tabla destino", choice(values, record["target"]))
            self.pairs_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            form.field("Origen → destino (MATCH SIMPLE)", self.pairs_box)
            self.pairs = None
            self._pairs_for_target(record["pairs"])
            self.target.connect("changed", lambda _c: self._pairs_for_target([]))
            self.on_delete = form.field("ON DELETE", enum(ACTIONS, record["on_delete"]))
            self.on_update = form.field("ON UPDATE", enum(ACTIONS, record["on_update"]))
        elif kind == "checks":
            widget, self.read_expression = text_area(record["expression"])
            form.field("Expresión SQL", widget)
        else:
            self.method = form.field("Método", enum(METHODS, record["method"]))
            self.unique = Gtk.CheckButton(label="UNIQUE", active=record["unique"])
            self.nulls = Gtk.CheckButton(label="NULLS NOT DISTINCT", active=record["nulls_not_distinct"])
            form.append(self.unique)
            form.append(self.nulls)
            self.entries = form.field("Campos ordenados: columna o expresión", Rows(record["entries"], self.local))
            self.include = form.field("INCLUDE", OrderedColumns(self.local, record["include"]))
            widget, self.read_predicate = text_area(record["predicate"])
            form.field("WHERE — predicado opcional", widget)
        form.append(label("Las expresiones SQL se conservan como texto; no se ejecutan ni validan contra PostgreSQL."))

    def _pairs_for_target(self, pairs):
        if self.pairs:
            self.pairs_box.remove(self.pairs)
        target = self.targets.get(self.target.get_active_id())
        if target is self.parent_editor.table:
            remote = self.local
        else:
            remote = [(c["id"], c["name"]) for c in snapshot(target)["columns"]] if target else []
        self.pairs = Rows(pairs, self.local, remote)
        self.pairs_box.append(self.pairs)

    def save(self):
        rec = deepcopy(self.record)
        rec["name"] = self.name.get_text()
        if not rec["name"].strip():
            self.error.set_text("Escribe un nombre.")
            return False
        kind = self.kind
        if kind == "columns":
            rec.update(type=self.type.get_child().get_text(), nullable=self.nullable.get_active(),
                       default=self.read_default(), identity=self.identity.get_active_id())
        elif kind == "keys":
            rec.update(kind=self.key_kind.get_active_id(), columns=list(self.columns.selected),
                       nulls_not_distinct=self.nulls.get_active())
        elif kind == "foreign_keys":
            rec.update(target=self.target.get_active_id() or "", pairs=self.pairs.read(),
                       on_delete=self.on_delete.get_active_id(), on_update=self.on_update.get_active_id())
        elif kind == "checks":
            rec["expression"] = self.read_expression()
        else:
            rec.update(method=self.method.get_active_id(), unique=self.unique.get_active(),
                       nulls_not_distinct=self.nulls.get_active(), entries=self.entries.read(),
                       include=list(self.include.selected), predicate=self.read_predicate())
        self.done(rec)
        self.cancel()
        return True


class RecordList(Gtk.Box):
    def __init__(self, editor, kind, title, create):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.editor, self.kind, self.create = editor, kind, create
        self.append(label(title))
        self.body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.append(self.body)
        self.append(button("Añadir", self.add))
        self.refresh()

    def summary(self, rec):
        if self.kind == "columns":
            return f"{rec['name']}: {rec['type']}" + ("  NOT NULL" if not rec["nullable"] else "")
        if self.kind == "checks":
            return f"{rec['name']}: {rec['expression']}"
        if self.kind == "keys":
            names = {c["id"]: c["name"] for c in self.editor.draft["columns"]}
            return f"{rec['name']}  {rec['kind']} ({', '.join(names.get(c, '?') for c in rec['columns'])})"
        if self.kind == "foreign_keys":
            target = self.editor.table.model.lookup(rec["target"])
            return f"{rec['name']} → {qualified_name(target) if target else '(sin destino)'}"
        return f"{rec['name']}  {rec['method']}" + (" UNIQUE" if rec["unique"] else "")

    def refresh(self):
        while child := self.body.get_first_child():
            self.body.remove(child)
        for index, rec in enumerate(self.editor.draft[self.kind]):
            row = Gtk.Box(spacing=5)
            text = label(self.summary(rec))
            text.set_hexpand(True)
            text.set_max_width_chars(60)
            text.set_ellipsize(Pango.EllipsizeMode.END)
            text.set_tooltip_text(self.summary(rec))
            row.append(text)
            row.append(button("Editar…", lambda rec=rec: self.edit(rec)))
            if self.kind == "columns":
                row.append(button("↑", lambda i=index: self.move(i, -1)))
                row.append(button("↓", lambda i=index: self.move(i, 1)))
            row.append(button("Quitar", lambda rec=rec: self.remove_record(rec)))
            self.body.append(row)

    def move(self, index, delta):
        records = self.editor.draft[self.kind]
        other = index + delta
        if 0 <= other < len(records):
            records[index], records[other] = records[other], records[index]
            self.refresh()

    def remove_record(self, rec):
        self.editor.draft[self.kind].remove(rec)
        self.editor.refresh()

    def add(self):
        self.edit(self.create(), is_new=True)

    def edit(self, rec, is_new=False):
        if self.editor.child and not self.editor.child.finished:
            self.editor.child.present()
            return
        def done(updated):
            records = self.editor.draft[self.kind]
            if is_new:
                records.append(updated)
            else:
                records[records.index(rec)] = updated
            self.editor.refresh()
        self.editor.child = RecordEditor(self.editor, self.kind, rec, done)
        self.editor.child.present()


class TableEditor(Modal):
    def __init__(self, parent, table, events, on_closed, after_save=None, notify=None):
        super().__init__(parent, f"Editar tabla — {qualified_name(table)}", 980, 740)
        self.table, self.events, self.on_closed = table, events, on_closed
        self.after_save, self.notify = after_save, notify
        self.expected = snapshot(table)
        self.draft = deepcopy(self.expected)
        self.child = None
        top = Form()
        self.name = top.field("Nombre de la tabla", entry(table.name))
        self.layout.prepend(top)
        self.tabs = Gtk.Notebook(vexpand=True)
        self.layout.insert_child_after(self.tabs, top)
        self.lists = {}
        for title, groups in (
            ("Columnas", (("columns", "Columnas", new_column),)),
            ("Claves y relaciones", (("keys", "Claves primarias y únicas", new_key), ("foreign_keys", "Claves foráneas", new_fk))),
            ("Restricciones", (("checks", "CHECK", new_check),)),
            ("Índices", (("indexes", "Índices", new_index),)),
        ):
            form = Form()
            for kind, heading, create in groups:
                listing = self.lists[kind] = RecordList(self, kind, heading, create)
                form.append(listing)
            scroll = Gtk.ScrolledWindow(vexpand=True)
            scroll.set_child(form)
            self.tabs.append_page(scroll, Gtk.Label(label=title))
        self.layout.append(label("Guardar aplica al modelo en memoria. Guarda después el proyecto con Ctrl+S. Quitar elementos usados por otras restricciones impedirá guardar."))

    def refresh(self):
        for listing in self.lists.values():
            listing.refresh()

    def save(self):
        self.draft["name"] = self.name.get_text()
        try:
            with Transaction(self.events):
                warnings = save_table(self.table, self.draft, self.events, self.expected)
                if self.after_save:
                    self.after_save(self.table)
        except (ModelError, ValueError, TypeError) as error:
            self.error.set_text(str(error))
            return False
        except Exception:
            log.exception("No se pudo guardar la tabla")
            self.error.set_text("No se pudo guardar. El borrador se conserva; consulta los diagnósticos de Gaphor.")
            return False
        if self.notify and warnings:
            self.notify("\n".join(dict.fromkeys(warnings)))
        self.cancel()
        return True

    def cancel(self):
        if self.finished:
            return
        if self.child and not self.child.finished:
            self.child.cancel()
        super().cancel()
        self.on_closed(self)
