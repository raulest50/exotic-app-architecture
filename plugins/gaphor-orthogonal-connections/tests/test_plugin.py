import asyncio
import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from gi.repository import Gdk, GLib, Gtk
from gaphor import UML
from gaphor.core import Transaction
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import ElementFactory
from gaphor.core.modeling.elementdispatcher import ElementDispatcher
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.services.undomanager import UndoManager
from gaphor.storage.load import load
from gaphor.storage.save import save
from gaphor.UML.classes.component import ComponentItem
from gaphor.UML.classes.package import PackageItem
from gaphor.UML.deployments.artifact import ArtifactItem
from gaphor.ui.diagrampage import DiagramPage
from gaphor.ui.event import CurrentDiagramChanged
from gaphor.ui.menufragment import MenuFragment

from gaphor_orthogonal_connections import OrthogonalConnections
from gaphor_orthogonal_connections.routing import Route, simplify


def drain():
    context = GLib.MainContext.default()
    for _ in range(10):
        if not context.pending():
            break
        context.iteration(False)


def points(item):
    return [tuple(map(float, h.pos)) for h in item.handles()]


class RoutingTests(unittest.TestCase):
    def test_default_and_flipped(self):
        route = Route()
        self.assertEqual(route.points((10, 20), (200, 300)), [(10, 20), (200, 20), (200, 300)])
        route.flip()
        self.assertEqual(route.points((10, 20), (200, 300)), [(10, 20), (10, 300), (200, 300)])

    def test_fixed_prefix_survives_flip_and_movement(self):
        route = Route()
        route.fix((10, 20), (100, 200))
        route.flip()
        result = route.points((10, 20), (300, 400))
        self.assertEqual(result, [(10, 20), (100, 20), (100, 400), (300, 400)])
        route.fix((10, 20), (300, 400))
        route.flip()
        self.assertIn((100, 20), route.points((10, 20), (-50, -50)))

    def test_duplicates_collinear_and_turns(self):
        self.assertEqual(simplify([(0, 0), (0, 0), (10, 0), (20, 0)]), [(0, 0), (20, 0)])
        self.assertEqual(simplify([(0, 0), (20, 0), (10, 0)]), [(0, 0), (20, 0), (10, 0)])


class InteractionTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        Gtk.init()
        self.events = EventManager()
        self.language = ModelingLanguageService(self.events)
        self.dispatcher = ElementDispatcher(self.events, self.language)
        self.model = ElementFactory(self.events, self.dispatcher)
        self.undo = UndoManager(self.events, self.model)
        self.service = OrthogonalConnections(MenuFragment(), self.events)
        with Transaction(self.events):
            self.diagram = self.model.create(UML.ComponentDiagram)
            self.diagram.name = "Temporal"
            self.source = self.diagram.create(ArtifactItem, subject=self.model.create(UML.Artifact))
            self.source.subject.name = "Origen.tsx"
            self.source.width, self.source.height = 150, 80
            self.source.matrix.translate(50, 50)
            self.target = self.diagram.create(ComponentItem, subject=self.model.create(UML.Component))
            self.target.subject.name = "Destino"
            self.target.width, self.target.height = 150, 100
            self.target.matrix.translate(450, 300)
        self.page = DiagramPage(self.diagram, self.events, self.model, self.language)
        self.widget = self.page.construct()
        self.view = self.page.view
        self.window = Gtk.Window()
        self.window.set_default_size(900, 650)
        self.window.set_child(self.widget)
        self.service.set_enabled(True)
        self.page.select_tool("toolbox-dependency")
        self.diagram.update(self.diagram.get_all_items())
        drain()
        await asyncio.sleep(0.01)
        self.undo.clear_undo_stack()
        self.before = self.model.size()

    async def asyncTearDown(self):
        self.service.shutdown()
        self.page.close()
        self.window.set_child(None)
        self.window.destroy()
        drain()
        await asyncio.sleep(0.01)
        self.undo.shutdown()
        self.model.shutdown()
        self.dispatcher.shutdown()
        self.language.shutdown()

    @property
    def drawing(self):
        return next(d for d in self.service.drawings if not d.closed)

    def pos(self, item, x, y):
        return self.view.get_matrix_i2v(item).transform_point(x, y)

    def begin(self):
        drawing = self.drawing
        start = self.pos(self.source, self.source.width, 40)
        self.fake = SimpleNamespace(set_state=lambda state: None, get_start_point=lambda: (True, *start))
        drawing._begin(self.fake, *start)
        self.assertIsNotNone(drawing.tx, "No se inició el trazado")
        return drawing

    def destination(self):
        return self.pos(self.target, 0, 40)

    def assert_axial(self, item):
        self.assertTrue(all(abs(a[0]-b[0]) < 0.001 or abs(a[1]-b[1]) < 0.001
                            for a,b in zip(points(item), points(item)[1:])), points(item))

    async def test_connect_direction_orthogonal_undo_redo(self):
        drawing = self.begin()
        drawing.move(self.destination())
        item = drawing.item
        self.assertTrue(drawing.finish(self.destination()))
        self.assertIn(self.source.subject, item.subject.client)
        self.assertIn(self.target.subject, item.subject.supplier)
        self.assertTrue(item.orthogonal)
        self.assert_axial(item)
        saved_points = points(item)
        item_id = item.id
        self.undo.undo_transaction()
        self.assertEqual(self.model.size(), self.before)
        self.assertIsNone(self.model.lookup(item_id))
        self.undo.redo_transaction()
        restored = self.model.lookup(item_id)
        self.assertEqual(points(restored), saved_points)
        self.assert_axial(restored)

    async def test_space_tab_repeat_and_multiple_waypoints(self):
        drawing = self.begin()
        drawing.move((280, 200))
        self.assertTrue(drawing.keys.emit("key-pressed", Gdk.KEY_space, 32, Gdk.ModifierType(0)))
        drawing.keys.emit("key-pressed", Gdk.KEY_space, 32, Gdk.ModifierType(0))
        self.assertEqual(len(drawing.route.legs), 1)
        drawing.keys.emit("key-released", Gdk.KEY_space, 32, Gdk.ModifierType(0))
        drawing.move((350, 250))
        drawing.keys.emit("key-pressed", Gdk.KEY_Tab, 9, Gdk.ModifierType(0))
        drawing.keys.emit("key-pressed", Gdk.KEY_Tab, 9, Gdk.ModifierType(0))
        self.assertFalse(drawing.route.horizontal)
        drawing.keys.emit("key-released", Gdk.KEY_Tab, 9, Gdk.ModifierType(0))
        drawing.keys.emit("key-pressed", Gdk.KEY_space, 32, Gdk.ModifierType(0))
        self.assertEqual(len(drawing.route.legs), 2)
        item = drawing.item
        self.assertTrue(drawing.finish(self.destination()))
        self.assertGreaterEqual(len(points(item)), 5)
        self.assert_axial(item)

    async def test_escape_rollback_and_no_undo_entry(self):
        drawing = self.begin()
        drawing.move((300, 200))
        drawing.keys.emit("key-pressed", Gdk.KEY_Escape, 27, Gdk.ModifierType(0))
        self.assertIsNone(drawing.tx)
        self.assertFalse(Transaction.in_transaction())
        self.assertEqual(self.model.size(), self.before)
        drawing._end(self.fake, 200, 200)
        self.assertEqual(self.model.size(), self.before)

    async def test_invalid_target_rolls_back(self):
        drawing = self.begin()
        self.assertFalse(drawing.finish((800, 600)))
        self.assertEqual(self.model.size(), self.before)
        self.assertFalse(Transaction.in_transaction())

    async def test_blank_origin_does_not_create(self):
        self.drawing._begin(SimpleNamespace(set_state=lambda value: None), 800, 600)
        self.assertEqual(self.model.size(), self.before)
        self.assertFalse(Transaction.in_transaction())

    async def test_same_figure_cancels(self):
        drawing = self.begin()
        self.assertFalse(drawing.finish(self.pos(self.source, 0, 40)))
        self.assertEqual(self.model.size(), self.before)

    async def test_focus_loss_and_change_diagram(self):
        self.begin().focus.emit("leave")
        self.assertEqual(self.model.size(), self.before)
        self.begin()
        self.events.handle(CurrentDiagramChanged(None))
        self.assertEqual(self.model.size(), self.before)
        self.assertFalse(Transaction.in_transaction())

    async def test_exception_during_route_rolls_back(self):
        self.begin()
        with self.assertLogs("gaphor_orthogonal_connections.interaction", level="ERROR"), patch("gaphor_orthogonal_connections.interaction.set_points", side_effect=ValueError("test")):
            self.drawing._update(self.fake, 100, 100)
        self.assertFalse(Transaction.in_transaction())
        self.assertEqual(self.model.size(), self.before)

    async def test_zoom_pan_and_nested_package(self):
        with Transaction(self.events):
            package = self.model.create(UML.Package)
            package.name = "Paquete"
            container = self.diagram.create(PackageItem, subject=package)
            container.width, container.height = 800, 550
            container.matrix.translate(20, 30)
            self.source.change_parent(container)
            self.source.subject.package = package
        self.view.matrix.set(1.6, 0, 0, 1.6, -20, 40)
        self.diagram.update(self.diagram.get_all_items())
        drain()
        await asyncio.sleep(0.01)
        drawing = self.begin()
        drawing.move(self.destination())
        item = drawing.item
        self.assertTrue(drawing.finish(self.destination()))
        self.assert_axial(item)

    async def test_save_reopen_native_points(self):
        drawing = self.begin()
        drawing.move((280, 230))
        drawing.route.fix(tuple(drawing.item.tail.pos), tuple(drawing.item.head.pos))
        item = drawing.item
        self.assertTrue(drawing.finish(self.destination()))
        original = points(item)
        stream = io.StringIO()
        save(stream, self.model)
        xml = stream.getvalue()
        self.assertNotIn("gaphor_orthogonal_connections", xml)
        reopened = ElementFactory(self.events, self.dispatcher)
        try:
            load(io.StringIO(xml), reopened, self.language)
            restored = reopened.lookup(item.id)
            restored.diagram.update(restored.diagram.get_all_items())
            self.assertEqual(points(restored), original)
            self.assertTrue(restored.orthogonal)
        finally:
            reopened.shutdown()

    async def test_disable_restores_native_tool_and_keys(self):
        old = self.drawing
        self.service.set_enabled(False)
        self.assertTrue(old.closed)
        self.assertFalse(old.keys.emit("key-pressed", Gdk.KEY_Tab, 9, Gdk.ModifierType(0)))
        self.assertEqual(len(self.service.drawings), 0)

    async def test_two_sessions_and_shutdown(self):
        other_events = EventManager()
        other = OrthogonalConnections(MenuFragment(), other_events)
        try:
            self.assertFalse(other.enabled)
            self.assertTrue(self.service.enabled)
            other.shutdown()
            drawing = self.begin()
            self.assertTrue(drawing.finish(self.destination()))
        finally:
            other.shutdown()

    async def test_other_tools_keep_native_controllers(self):
        old = self.drawing
        self.page.select_tool("toolbox-pointer")
        self.assertTrue(old.closed)
        self.assertFalse(self.service.drawings)

    async def test_incompatible_version_leaves_hooks_and_menu_unchanged(self):
        original = DiagramPage.apply_tool_set
        menu = MenuFragment()
        with self.assertLogs("gaphor_orthogonal_connections", level="WARNING"), patch("gaphor_orthogonal_connections.version", return_value="9.0"):
            other = OrthogonalConnections(menu, EventManager())
        try:
            self.assertFalse(other.compatible)
            other.set_enabled(True)
            self.assertFalse(other.enabled)
            self.assertIs(DiagramPage.apply_tool_set, original)
        finally:
            other.shutdown()

    async def test_fixed_bends_survive_final_constraints(self):
        drawing = self.begin()
        drawing.move((320, 240))
        drawing.route.fix(tuple(drawing.item.tail.pos), tuple(drawing.item.head.pos))
        drawing.move((260, 170))
        drawing.route.fix(tuple(drawing.item.tail.pos), tuple(drawing.item.head.pos))
        drawing.move(self.destination())
        item = drawing.item
        expected = points(item)
        self.assertTrue(drawing.finish(self.destination()))
        self.assertEqual(points(item), expected)

    async def test_straight_and_vertical_routes(self):
        for dx, dy in ((450, 50), (50, 350)):
            with Transaction(self.events):
                self.target.matrix.set(1, 0, 0, 1, dx, dy)
                self.diagram.update(self.diagram.get_all_items())
            await asyncio.sleep(0.01)
            drawing = self.begin()
            item = drawing.item
            self.assertTrue(drawing.finish(self.destination()))
            self.assert_axial(item)

    async def test_mode_toggle_leaves_saved_connections_untouched(self):
        drawing = self.begin()
        item = drawing.item
        self.assertTrue(drawing.finish(self.destination()))
        before = points(item)
        model_size = self.model.size()
        self.service.set_enabled(False)
        self.service.set_enabled(True)
        self.assertEqual(points(item), before)
        self.assertEqual(self.model.size(), model_size)

    async def test_backtracking_does_not_shift_fixed_points(self):
        drawing = self.begin()
        drawing.move((320, 90))
        drawing.route.fix(tuple(drawing.item.tail.pos), tuple(drawing.item.head.pos))
        drawing.move((260, 90))
        drawing.route.fix(tuple(drawing.item.tail.pos), tuple(drawing.item.head.pos))
        drawing.move(self.destination())
        item = drawing.item
        expected = points(item)
        self.assertTrue(drawing.finish(self.destination()))
        self.assertEqual(points(item), expected)

    async def test_cancel_restores_selection_and_notifies_other_plugins(self):
        from gaphor.core import event_handler
        from gaphor.diagram.event import DiagramSelectionChanged
        received = []
        @event_handler(DiagramSelectionChanged)
        def selected(event):
            received.append(event.focused_item)
        self.events.subscribe(selected)
        self.view.selection.select_items(self.source)
        self.view.selection.focused_item = self.source
        self.begin().cancel()
        self.assertIs(self.view.selection.focused_item, self.source)
        self.assertIs(received[-1], self.source)
        self.events.unsubscribe(selected)

