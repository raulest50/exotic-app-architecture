"""Modal folder selection, cancellable analysis and explicit snapshot generation."""

import logging
from pathlib import Path
from threading import Event, Thread

from gi.repository import Gdk, Gio, GLib, Gtk
from gaphor import UML

from .model import create_capture, package_path
from .scanner import DEFAULT_EXCLUSIONS, ScanCancelled, ScanError, parse_exclusions, scan_folder

TITLE = "Importar/leer componente en crudo…"
log = logging.getLogger(__name__)


class ImportWindow(Gtk.Window):
    def __init__(self, parent, model, event_manager, destination, on_created, on_closed):
        super().__init__(title=TITLE, transient_for=parent, modal=True, resizable=True,
                         default_width=720, default_height=450)
        self.model = model
        self.event_manager = event_manager
        self.on_created = on_created
        self.on_closed = on_closed
        self.closed = False
        self.snapshot = None
        self.scan_cancel = None
        self.chooser_cancel = None
        self.epoch = 0
        self.worker = None

        header = Gtk.HeaderBar()
        cancel = Gtk.Button(label="Cancelar")
        cancel.connect("clicked", lambda _button: self.cancel())
        self.generate_button = Gtk.Button(label="Generar", sensitive=False)
        self.generate_button.add_css_class("suggested-action")
        self.generate_button.connect("clicked", lambda _button: self.generate())
        header.pack_start(cancel)
        header.pack_end(self.generate_button)
        self.set_titlebar(header)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        for side in ("top", "bottom", "start", "end"):
            getattr(box, f"set_margin_{side}")(20)
        box.append(Gtk.Label(label="Carpeta de origen", xalign=0))
        row = Gtk.Box(spacing=8)
        self.folder = Gtk.Entry(hexpand=True, placeholder_text="Selecciona una carpeta")
        self.folder.connect("changed", self._invalidate)
        row.append(self.folder)
        self.choose_button = Gtk.Button(label="Elegir carpeta…")
        self.choose_button.connect("clicked", self.choose_folder)
        row.append(self.choose_button)
        box.append(row)
        box.append(Gtk.Label(label="Paquete destino", xalign=0))
        self.destinations = [None] + sorted(
            (p for p in model.select(UML.Package) if type(p) is UML.Package),
            key=lambda p: (package_path(p).casefold(), p.id),
        )
        labels = ["Raíz del modelo"]
        paths = [package_path(p) for p in self.destinations[1:]]
        labels.extend(path if paths.count(path) == 1 else f"{path} [{p.id[:8]}]"
                      for p, path in zip(self.destinations[1:], paths))
        self.destination = Gtk.DropDown.new_from_strings(labels)
        self.destination.set_enable_search(True)
        self.destination.set_selected(self.destinations.index(destination) if destination in self.destinations else 0)
        box.append(self.destination)
        box.append(Gtk.Label(label="Excluir carpetas (nombres separados por comas)", xalign=0))
        self.exclusions = Gtk.Entry(text=", ".join(DEFAULT_EXCLUSIONS))
        self.exclusions.connect("changed", self._invalidate)
        box.append(self.exclusions)
        row = Gtk.Box(spacing=12)
        self.analyze_button = Gtk.Button(label="Analizar")
        self.analyze_button.connect("clicked", lambda _button: self.analyze())
        self.spinner = Gtk.Spinner()
        row.append(self.analyze_button)
        row.append(self.spinner)
        box.append(row)
        self.summary = Gtk.Label(label="Analiza la carpeta para revisar las cantidades antes de generar.", xalign=0, wrap=True, selectable=True)
        box.append(self.summary)
        hint = Gtk.Label(label="Cada lectura crea una captura nueva. Los enlaces no se recorren.\nDespués de generar, guarda el proyecto como de costumbre.", xalign=0, wrap=True)
        hint.add_css_class("dim-label")
        box.append(hint)
        scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        scroll.set_child(box)
        self.set_child(scroll)
        self.connect("close-request", self._close_request)
        keys = Gtk.EventControllerKey.new()
        keys.connect("key-pressed", self._key_pressed)
        self.add_controller(keys)

    def _invalidate(self, _entry=None):
        self.epoch += 1
        if self.scan_cancel:
            self.scan_cancel.set()
            self.scan_cancel = None
        self.snapshot = None
        self.generate_button.set_sensitive(False)
        self.analyze_button.set_sensitive(True)
        self.spinner.stop()
        self.summary.set_text("Origen o exclusiones modificados. Pulsa Analizar.")

    def choose_folder(self, _button=None):
        self.chooser_cancel = Gio.Cancellable()
        dialog = Gtk.FileDialog(title="Seleccionar carpeta de origen", modal=True)
        self.choose_button.set_sensitive(False)
        dialog.select_folder(self, self.chooser_cancel, self._folder_selected)

    def _folder_selected(self, dialog, result):
        if self.closed:
            return
        self.choose_button.set_sensitive(True)
        self.chooser_cancel = None
        try:
            chosen = dialog.select_folder_finish(result)
            if chosen and chosen.get_path():
                self.folder.set_text(chosen.get_path())
            elif chosen:
                self.summary.set_text("Selecciona una carpeta disponible en el sistema de archivos local.")
        except GLib.Error as error:
            if not error.matches(Gtk.dialog_error_quark(), Gtk.DialogError.DISMISSED) and not error.matches(Gio.io_error_quark(), Gio.IOErrorEnum.CANCELLED):
                self.summary.set_text(f"No se pudo seleccionar la carpeta: {error.message}")

    def analyze(self):
        self._invalidate()
        folder = self.folder.get_text()
        try:
            if not folder.strip():
                raise ScanError("Selecciona una carpeta de origen.")
            exclusions = parse_exclusions(self.exclusions.get_text())
        except ScanError as error:
            self.summary.set_text(str(error))
            return
        token = self.scan_cancel = Event()
        epoch = self.epoch
        self.analyze_button.set_sensitive(False)
        self.spinner.start()
        self.summary.set_text("Analizando nombres de archivos y carpetas… Puedes cancelar.")

        def work():
            result, error = None, None
            try:
                result = scan_folder(Path(folder), exclusions, token)
            except ScanCancelled:
                return
            except Exception as exception:
                error = exception
                if not isinstance(exception, ScanError):
                    log.exception("Error al analizar la carpeta")
            if not token.is_set():
                GLib.idle_add(self._analysis_done, epoch, result, error)

        self.worker = Thread(target=work, name="gaphor-folder-scan", daemon=True)
        self.worker.start()

    def _analysis_done(self, epoch, result, error):
        if self.closed or epoch != self.epoch:
            return GLib.SOURCE_REMOVE
        self.spinner.stop()
        self.scan_cancel = None
        self.analyze_button.set_sensitive(True)
        if error:
            self.summary.set_text(str(error))
            return GLib.SOURCE_REMOVE
        self.snapshot = result
        self.summary.set_text(
            f"{result.files} archivos · {result.directories} carpetas (incluida la raíz)\n"
            f"{result.excluded} carpetas excluidas · {result.links} enlaces/uniones omitidos"
            + (f" · {result.special} entradas especiales omitidas" if result.special else "")
        )
        self.generate_button.set_sensitive(True)
        return GLib.SOURCE_REMOVE

    def generate(self):
        if self.closed or self.snapshot is None:
            return False
        self.generate_button.set_sensitive(False)
        index = self.destination.get_selected()
        destination = self.destinations[index]
        try:
            capture = create_capture(self.model, self.event_manager, self.snapshot, destination)
        except Exception as error:
            log.exception("No se pudo crear la captura")
            self.summary.set_text(f"No se creó la captura: {error}")
            self.generate_button.set_sensitive(True)
            return False
        self.cancel()
        # The transaction is already committed: a view error must not offer to generate twice.
        self.on_created(capture)
        return True

    def cancel(self):
        if self.closed:
            return
        self.closed = True
        self.epoch += 1
        if self.scan_cancel:
            self.scan_cancel.set()
        if self.chooser_cancel:
            self.chooser_cancel.cancel()
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
