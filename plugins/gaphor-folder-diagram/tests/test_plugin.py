import io
import os
from pathlib import Path
import stat
import sys
import tempfile
from threading import Event
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from gi.repository import Gdk, Gio, GLib, Gtk
from gaphas.matrix import Matrix
from gaphor import UML
from gaphor.core import Transaction
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import ElementFactory, StyleSheet
from gaphor.core.modeling.elementdispatcher import ElementDispatcher
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.services.undomanager import UndoManager
from gaphor.storage.load import load
from gaphor.storage.save import save
from gaphor.diagram.export import save_png
from gaphor.diagram.event import DiagramSelectionChanged
from gaphor.ui.event import CurrentDiagramChanged, ModelSelectionChanged
from gaphor.ui.menufragment import MenuFragment

from gaphor_folder_diagram import FolderDiagramService
from gaphor_folder_diagram.model import ImportError, create_capture, validate_layout
from gaphor_folder_diagram.scanner import Entry, Snapshot, ScanError, ScanCancelled, _link, parse_exclusions, scan_folder
from gaphor_folder_diagram.ui import ImportWindow


def drain():
    context = GLib.MainContext.default()
    while context.pending():
        context.iteration(False)


class PluginTests(unittest.TestCase):
    def setUp(self):
        Gtk.init()
        self.temporary = tempfile.TemporaryDirectory(prefix="gaphor-folder-fixture-")
        self.root = Path(self.temporary.name) / "main-folder"
        (self.root / "level2").mkdir(parents=True)
        for file in ("archivo1.ts", "archivo2.ts", "archivo3.ts", "level2/archivo4.ts", "level2/archivo5.ts"):
            (self.root / file).write_bytes(b"Not parsed\x00\xff")
        self.events = EventManager()
        self.language = ModelingLanguageService(self.events)
        self.dispatcher = ElementDispatcher(self.events, self.language)
        self.model = ElementFactory(self.events, self.dispatcher)
        self.undo = UndoManager(self.events, self.model)
        self.windows = []
        self.services = []

    def tearDown(self):
        for window in self.windows:
            window.cancel()
            if window.worker:
                window.worker.join(3)
        for service in self.services:
            service.shutdown()
        drain()
        self.undo.shutdown()
        self.model.shutdown()
        self.dispatcher.shutdown()
        self.language.shutdown()
        self.temporary.cleanup()

    def capture(self, destination=None):
        return create_capture(self.model, self.events, scan_folder(self.root), destination)

    def window(self):
        window = ImportWindow(None, self.model, self.events, None, Mock(), Mock())
        self.windows.append(window)
        window.folder.set_text(str(self.root))
        return window

    def analyzed(self, window):
        window.analyze()
        window.worker.join(5)
        self.assertFalse(window.worker.is_alive())
        drain()
        self.assertIsNotNone(window.snapshot, window.summary.get_text())

    def selection_service(self):
        service = FolderDiagramService(SimpleNamespace(window=None), MenuFragment(),
                                       self.events, self.model, Mock())
        self.services.append(service)
        return service

    def assert_import_destination(self, service, destination):
        with patch("gaphor_folder_diagram.ImportWindow") as window:
            service.import_raw_component()
            self.assertIs(window.call_args.args[3], destination)
            service.window = None

    def test_five_files_two_directories_and_no_contents_read(self):
        with patch("builtins.open", side_effect=AssertionError("No content reads")):
            snapshot = scan_folder(self.root)
        self.assertEqual((snapshot.files, snapshot.directories), (5, 2))
        self.assertEqual([e.name for e in snapshot.root.children], ["archivo1.ts", "archivo2.ts", "archivo3.ts", "level2"])

    def test_exclusions_at_any_depth_but_files_and_hidden_names_included(self):
        for folder in ("node_modules", "level2/dist", ".git", "empty"):
            (self.root / folder).mkdir()
        (self.root / ".hidden").write_text("", encoding="utf-8")
        (self.root / "build").write_text("file, not directory", encoding="utf-8")
        snapshot = scan_folder(self.root)
        self.assertEqual((snapshot.files, snapshot.directories, snapshot.excluded), (7, 3, 3))
        complete = scan_folder(self.root, exclusions=())
        self.assertEqual((complete.directories, complete.excluded), (6, 0))

    def test_invalid_exclusion_is_actionable(self):
        self.assertEqual(parse_exclusions("dist, build;\n.venv"), {"dist", "build", ".venv"})
        for value in ("a/b", "a\\b", "*.ts", ".."):
            with self.assertRaises(ScanError):
                parse_exclusions(value)

    def test_cancelled_scan(self):
        cancel = Event()
        cancel.set()
        with self.assertRaises(ScanCancelled):
            scan_folder(self.root, cancel=cancel)

    def test_permission_error_does_not_produce_partial_snapshot(self):
        original = os.scandir
        def denied(path):
            if Path(path).name == "level2":
                raise PermissionError(13, "Access denied", str(path))
            return original(path)
        with patch("gaphor_folder_diagram.scanner.os.scandir", side_effect=denied):
            with self.assertRaisesRegex(ScanError, "level2"):
                scan_folder(self.root)
        self.assertEqual(self.model.size(), 0)

    def test_reparse_points_and_symlinks_are_detected(self):
        self.assertTrue(_link(SimpleNamespace(st_mode=stat.S_IFLNK)))
        self.assertTrue(_link(SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)))
        self.assertFalse(_link(SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0)))
        fake = Mock()
        fake.name = "link-loop"
        fake.stat.return_value = SimpleNamespace(st_mode=stat.S_IFLNK)
        listing = Mock()
        listing.__enter__ = Mock(return_value=iter([fake]))
        listing.__exit__ = Mock(return_value=False)
        with patch("gaphor_folder_diagram.scanner.os.scandir", return_value=listing):
            snapshot = scan_folder(self.root)
        self.assertEqual((snapshot.links, snapshot.files, snapshot.directories), (1, 0, 1))

    def test_invalid_root(self):
        for path in (self.root / "missing", self.root / "archivo1.ts"):
            with self.assertRaises(ScanError):
                scan_folder(path)

    def test_hierarchy_and_only_one_diagram(self):
        capture = self.capture()
        self.assertEqual(capture.package.name, "Lectura main-folder")
        self.assertIs(capture.elements.nestingPackage, capture.package)
        self.assertIs(capture.diagram.element, capture.package)
        self.assertIs(capture.root_item.subject.nestingPackage, capture.elements)
        self.assertEqual(len(list(self.model.select(UML.ComponentDiagram))), 1)
        self.assertEqual(len(list(self.model.select(UML.Artifact))), 5)
        self.assertEqual(len(list(capture.diagram.get_all_items())), 7)
        for item in capture.diagram.get_all_items():
            if item.parent:
                self.assertIs(item.subject.owner, item.parent.subject)
        validate_layout(capture.diagram)

    def test_empty_folder_is_visible(self):
        root = self.root / "empty"
        root.mkdir()
        capture = create_capture(self.model, self.events, scan_folder(root))
        self.assertEqual(len(list(capture.diagram.get_all_items())), 1)
        self.assertGreater(capture.root_item.height, 64)

    def test_long_names_unicode_duplicate_names_and_deep_nesting(self):
        (self.root / "level2" / "archivo1.ts").write_text("", encoding="utf-8")
        (self.root / ("Descripción_" + "NombreLargo_" * 12 + ".tsx")).write_text("", encoding="utf-8")
        deepest = self.root / "uno" / "dos" / "tres" / "cuatro"
        deepest.mkdir(parents=True)
        (deepest / "archivo1.ts").write_text("", encoding="utf-8")
        capture = self.capture()
        artifacts = list(self.model.select(UML.Artifact))
        duplicates = [a for a in artifacts if a.name == "archivo1.ts"]
        self.assertEqual(len({a.package for a in duplicates}), 3)
        long_item = next(i for i in capture.diagram.get_all_items() if i.subject.name.startswith("Descripción_"))
        self.assertGreater(long_item.width, 400)
        validate_layout(capture.diagram)

    def test_new_capture_numbered_per_destination(self):
        first, second = self.capture(), self.capture()
        self.assertEqual(second.package.name, "Lectura main-folder (2)")
        self.assertEqual(first.package.name, "Lectura main-folder")
        third = self.capture(first.package)
        self.assertEqual(third.package.name, "Lectura main-folder")
        self.assertIs(third.package.nestingPackage, first.package)

    def test_single_undo_redo_restores_model_and_geometry(self):
        capture = self.capture()
        original = {i.id: (tuple(i.matrix), i.width, i.height) for i in capture.diagram.get_all_items()}
        self.undo.undo_transaction()
        self.assertEqual(self.model.size(), 0)
        self.undo.redo_transaction()
        diagram = self.model.lookup(capture.diagram.id)
        self.assertEqual(original, {i.id: (tuple(i.matrix), i.width, i.height) for i in diagram.get_all_items()})
        validate_layout(diagram)

    def test_generation_failure_rolls_back_everything(self):
        with patch("gaphor_folder_diagram.model.validate_layout", side_effect=ImportError("Overlap")):
            with self.assertRaises(ImportError):
                self.capture()
        self.assertEqual(self.model.size(), 0)

    def test_stale_destination_rejected(self):
        with Transaction(self.events):
            destination = self.model.create(UML.Package)
            destination.unlink()
        with self.assertRaises(ImportError):
            self.capture(destination)
        self.assertEqual(self.model.size(), 0)

    def test_layout_validation_rejects_overlap(self):
        capture = self.capture()
        children = list(capture.root_item.children)
        with Transaction(self.events):
            children[1].matrix.set(*children[0].matrix)
        with self.assertRaises(ImportError):
            validate_layout(capture.diagram)

    def test_save_reopen_geometry_and_native_objects(self):
        capture = self.capture()
        stream = io.StringIO()
        save(stream, self.model)
        other = ElementFactory()
        load(io.StringIO(stream.getvalue()), other, self.language)
        diagram = other.lookup(capture.diagram.id)
        diagram.update(diagram.ownedPresentation)
        validate_layout(diagram)
        self.assertEqual(len(list(diagram.get_all_items())), 7)
        self.assertNotIn("gaphor_folder_diagram", stream.getvalue())

    def test_many_files_have_room(self):
        entry = Entry("large", True, tuple(Entry(f"file-{i:03}.tsx", False) for i in range(250)))
        capture = create_capture(self.model, self.events, Snapshot(entry, 250, 1, 0, 0, 0))
        validate_layout(capture.diagram)
        self.assertEqual(len(list(capture.diagram.get_all_items())), 251)

    def test_async_analysis_and_input_changes(self):
        window = self.window()
        self.analyzed(window)
        self.assertTrue(window.generate_button.get_sensitive())
        self.assertIn("5 archivos", window.summary.get_text())
        self.assertEqual(self.model.size(), 0)
        window.exclusions.set_text("level2")
        self.assertIsNone(window.snapshot)
        self.assertFalse(window.generate_button.get_sensitive())
        self.analyzed(window)
        self.assertEqual(window.snapshot.files, 3)
        window.folder.set_text(str(self.root / "level2"))
        self.assertIsNone(window.snapshot)

    def test_cancel_during_analysis_and_stale_worker_ignored(self):
        window = self.window()
        def wait_for_cancel(folder, exclusions, token):
            token.wait(2)
            raise ScanCancelled()
        with patch("gaphor_folder_diagram.ui.scan_folder", side_effect=wait_for_cancel):
            window.analyze()
            epoch = window.epoch
            window.cancel()
            window.worker.join(3)
        window._analysis_done(epoch, scan_folder(self.root), None)
        self.assertIsNone(window.snapshot)
        self.assertEqual(self.model.size(), 0)

    def test_dialog_cancel_and_generation(self):
        cancelled = self.window()
        self.analyzed(cancelled)
        cancelled._key_pressed(None, Gdk.KEY_Escape, 0, 0)
        self.assertEqual(self.model.size(), 0)
        window = self.window()
        self.analyzed(window)
        self.assertTrue(window.generate())
        self.assertTrue(window.closed)
        window.on_created.assert_called_once()
        self.assertFalse(window.generate())

    def test_folder_chooser_selection_cancellation_and_closed_callback(self):
        window = self.window()
        self.analyzed(window)
        chooser = Mock()
        chooser.select_folder_finish.return_value = Gio.File.new_for_path(str(self.root / "level2"))
        with patch("gaphor_folder_diagram.ui.Gtk.FileDialog", return_value=chooser):
            window.choose_folder()
        self.assertFalse(window.choose_button.get_sensitive())
        self.assertIs(chooser.select_folder.call_args.args[0], window)
        window._folder_selected(chooser, None)
        self.assertEqual(window.folder.get_text(), str(self.root / "level2"))
        self.assertIsNone(window.snapshot)
        self.assertTrue(window.choose_button.get_sensitive())
        self.assertFalse(window.generate_button.get_sensitive())
        chooser.select_folder_finish.side_effect = GLib.Error.new_literal(
            Gtk.dialog_error_quark(), "Dismissed", Gtk.DialogError.DISMISSED
        )
        window._folder_selected(chooser, None)
        self.assertEqual(window.folder.get_text(), str(self.root / "level2"))
        with patch("gaphor_folder_diagram.ui.Gtk.FileDialog", return_value=chooser):
            window.choose_folder()
        cancellable = window.chooser_cancel
        window.cancel()
        self.assertTrue(cancellable.is_cancelled())
        chooser.select_folder_finish.reset_mock()
        window._folder_selected(chooser, None)
        chooser.select_folder_finish.assert_not_called()

    def test_created_diagram_fits_view_and_does_not_move_another_diagram(self):
        capture = self.capture()
        view = Mock()
        view.get_width.return_value = 800
        view.get_height.return_value = 600
        view.matrix = Matrix()
        diagrams = Mock()
        diagrams.get_current_diagram.return_value = capture.diagram
        diagrams.get_current_view.return_value = view
        service = FolderDiagramService(SimpleNamespace(window=None), MenuFragment(),
                                       self.events, self.model, diagrams)
        self.services.append(service)
        with patch("gaphor_folder_diagram.GLib.timeout_add", return_value=0) as timeout:
            service._created(capture)
            fit = timeout.call_args.args[1]
            self.assertEqual(fit(), GLib.SOURCE_REMOVE)
        root = capture.root_item
        x, y = root.matrix.transform_point(0, 0)
        left, top = view.matrix.transform_point(x, y)
        right, bottom = view.matrix.transform_point(x + root.width, y + root.height)
        self.assertGreaterEqual(left, 32)
        self.assertGreaterEqual(top, 32)
        self.assertLessEqual(right, 800 - 32)
        self.assertLessEqual(bottom, 600 - 32)
        view.queue_draw.assert_called_once()
        diagrams.get_current_diagram.return_value = None
        before = tuple(view.matrix)
        self.assertEqual(fit(), GLib.SOURCE_REMOVE)
        self.assertEqual(tuple(view.matrix), before)

    def test_menu_selection_shutdown_and_sessions(self):
        menus = [MenuFragment(), MenuFragment()]
        services = []
        for menu in menus:
            service = FolderDiagramService(SimpleNamespace(window=None), menu, self.events, self.model, Mock())
            self.services.append(service)
            services.append(service)
            self.assertEqual(menu.menu.get_n_items(), 1)
            self.assertEqual(service.menu.get_n_items(), 1)
        with Transaction(self.events):
            destination = self.model.create(UML.Package)
            destination.name = "Destino"
        self.events.handle(ModelSelectionChanged(None, destination))
        with patch("gaphor_folder_diagram.ImportWindow") as window:
            services[0].import_raw_component()
            self.assertIs(window.call_args.args[3], destination)
            services[0].window = None
        services[0].shutdown()
        self.services.remove(services[0])
        self.assertEqual(menus[0].menu.get_n_items(), 0)
        self.assertEqual(menus[1].menu.get_n_items(), 1)

    def test_empty_diagram_selection_uses_view_model_as_destination(self):
        capture = self.capture()
        service = self.selection_service()
        event = DiagramSelectionChanged(SimpleNamespace(model=capture.diagram), None, set())
        self.events.handle(event)
        self.assertIs(service.focused, capture.diagram)
        self.assert_import_destination(service, capture.package)

    def test_focused_figure_takes_priority_over_diagram_destination(self):
        capture = self.capture()
        service = self.selection_service()
        item = next(i for i in capture.diagram.get_all_items()
                    if i.subject.name == "archivo4.ts")
        view = SimpleNamespace(model=capture.diagram)
        for source in (view, None):
            with self.subTest(view=source):
                self.events.handle(DiagramSelectionChanged(source, item, {item}))
                self.assertIs(service.focused, item)
                self.assert_import_destination(service, item.subject.package)

    def test_missing_view_or_diagram_clears_stale_selection_to_root(self):
        capture = self.capture()
        service = self.selection_service()
        for view in (None, SimpleNamespace(model=None), SimpleNamespace()):
            with self.subTest(view=view):
                self.events.handle(ModelSelectionChanged(None, capture.package))
                self.events.handle(DiagramSelectionChanged(view, None, set()))
                self.assertIsNone(service.focused)
                self.assert_import_destination(service, None)

    def test_diagram_switch_and_close_update_import_destination(self):
        first, second = self.capture(), self.capture()
        service = self.selection_service()
        for capture in (first, second, first):
            self.events.handle(CurrentDiagramChanged(capture.diagram))
            self.assert_import_destination(service, capture.package)
            self.events.handle(DiagramSelectionChanged(
                SimpleNamespace(model=capture.diagram), None, set()))
            self.assertIs(service.focused, capture.diagram)
            self.assert_import_destination(service, capture.package)
        self.events.handle(CurrentDiagramChanged(None))
        self.assert_import_destination(service, None)

    def test_native_zoom_css_refresh_and_two_projects_with_both_source_plugins(self):
        # Source integration before installation; the runner disables installed plugins.
        from gaphor.application import Session
        from gaphor.entrypoint import load_entry_points
        description_source = Path(__file__).resolve().parents[2] / "gaphor-description-editor"
        sys.path.insert(0, str(description_source))
        from gaphor_description_editor import DescriptionEditor
        from zoom_integration import assert_style_isolation, exercise_zoom
        sessions = []
        try:
            results = []
            services = dict(load_entry_points("gaphor.services"))
            services.update(folder_diagram=FolderDiagramService, description_editor=DescriptionEditor)
            for css in ("color: navy;", "color: maroon;"):
                session = Session(services=services)
                sessions.append(session)
                main_window = session.get_service("main_window")
                main_window.window = Gtk.Window()
                capture = create_capture(session.get_service("element_factory"),
                                         session.get_service("event_manager"), scan_folder(self.root))
                results.append(exercise_zoom(session, capture, css))
            assert_style_isolation(*results)
        finally:
            for session in sessions:
                session.shutdown()
            sys.path.remove(str(description_source))

    def test_write_portable_fixture_and_render(self):
        output = os.environ.get("GAPHOR_FOLDER_TEST_OUTPUT")
        if not output:
            self.skipTest("Runner output required")
        capture = self.capture()
        with Transaction(self.events):
            style = self.model.create(StyleSheet)
            style.styleSheet = "diagram { background-color: #ffffff; }"
        with (Path(output) / "portable.gaphor").open("w", encoding="utf-8") as stream:
            save(stream, self.model)
        save_png(str(Path(output) / "example.png"), capture.diagram)


if __name__ == "__main__":
    unittest.main()
