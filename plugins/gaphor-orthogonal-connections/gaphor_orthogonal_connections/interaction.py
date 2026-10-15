"""One native dependency and one undo transaction per drag."""

import logging

from gaphas.connector import ConnectionSink, Connector
from gaphas.handlemove import item_at_point
from gaphas.segment import Segment
from gaphas.tool import view_focus_tool
from gi.repository import Gdk, Gtk
from gaphor.core import Transaction
from gaphor.diagram.event import DiagramItemPlaced, DiagramSelectionChanged
from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.tools import add_basic_tools
from gaphor.diagram.tools.handlemove import LineHandleMove
from gaphor.diagram.tools.placement import create_item
from gaphor.event import Notification

from .routing import EPSILON, Route, native_points

log = logging.getLogger(__name__)


def set_points(item, points):
    """Retain native endpoint handles and reversible segment mutations."""
    points = native_points(list(reversed(points)))  # Supplier/head first.
    if len(points) < 2:
        points *= 2
    segment = Segment(item, item.diagram)
    while len(item.handles()) < len(points):
        segment.split_segment(0)
    while len(item.handles()) > len(points):
        segment.merge_segment(0)
    for handle, point in zip(item.handles(), points):
        handle.pos = point
    item.request_update()


class DrawingHandleMove(LineHandleMove):
    """Only connect to model figures; crossing another line is not a target.

    Delegates the allow/glue/connection semantics to the native connector.
    In particular, lines on top of a figure must not capture a new endpoint.
    """
    def glue(self, pos, distance=LineHandleMove.GLUE_DISTANCE):
        for candidate in item_at_point(self.view, pos, distance=distance, exclude=(self.item,)):
            if not isinstance(candidate, ElementPresentation) or candidate.subject is None:
                continue
            connector = Connector(self.item, self.handle, self.view.model.connections)
            sink = ConnectionSink(candidate)
            if connector.glue(sink):
                self.view.selection.dropzone_item = candidate
                return sink
        self.view.selection.dropzone_item = None
        return None


class Drawing:
    def __init__(self, view, factory, events, service):
        self.view = view
        self.factory = factory
        self.events = events
        self.service = service
        self.tx = None
        self.item = None
        self.moving = None
        self.route = Route()
        self.last_position = None
        self.pressed = set()
        self.previous_selection = ()
        self.previous_focus = None
        self.closed = False
        self.gesture = Gtk.GestureDrag.new()
        self.gesture.set_button(1)
        self.gesture.connect("drag-begin", self._begin)
        self.gesture.connect("drag-update", self._update)
        self.gesture.connect("drag-end", self._end)
        self.gesture.connect("cancel", self._cancel_gesture)
        self.keys = Gtk.EventControllerKey.new()
        self.keys.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.keys.connect("key-pressed", self._key_pressed)
        self.keys.connect("key-released", self._key_released)
        self.focus = Gtk.EventControllerFocus.new()
        self.focus.connect("leave", self._focus_left)
        self.unrealize_handler = view.connect("unrealize", self._unrealize)

    def _failure(self):
        log.exception("No se pudo completar la dependencia ortogonal")
        self.cancel()
        self.events.handle(Notification("No se pudo crear la conexión. Se canceló el trazado."))

    def _begin(self, gesture, x, y):
        try:
            if self.closed or not self.service.enabled or Transaction.in_transaction():
                gesture.set_state(Gtk.EventSequenceState.DENIED)
                return
            self.service.cancel_drawings(except_drawing=self)
            self.view.grab_focus()
            self.previous_selection = tuple(self.view.selection.selected_items)
            self.previous_focus = self.view.selection.focused_item
            self.route = Route()
            self.pressed.clear()
            self.tx = Transaction(self.events)
            self.item = create_item(self.view, self.factory, self.events, x, y)
            DrawingHandleMove(self.item, self.item.tail, self.view).connect((x, y))
            if not self.view.model.connections.get_connection(self.item.tail):
                self.cancel()
                gesture.set_state(Gtk.EventSequenceState.DENIED)
                return
            self.moving = DrawingHandleMove(self.item, self.item.head, self.view)
            self.moving.start_move((x, y))
            gesture.set_state(Gtk.EventSequenceState.CLAIMED)
            self.move((x, y))
        except Exception:
            self._failure()

    def move(self, position):
        self.last_position = position
        self.moving.move(position)
        self._route()

    def _route(self):
        points = self.route.points(tuple(self.item.tail.pos), tuple(self.item.head.pos))
        set_points(self.item, points)
        self.view.model.update({self.item})

    def _update(self, gesture, dx, dy):
        if self.tx:
            try:
                _, x, y = gesture.get_start_point()
                self.move((x + dx, y + dy))
            except Exception:
                self._failure()

    def _end(self, gesture, dx, dy):
        if not self.tx:
            return
        try:
            _, x, y = gesture.get_start_point()
            self.finish((x + dx, y + dy))
        except Exception:
            self._failure()

    def finish(self, position):
        self.move(position)
        self.moving.stop_move(position)
        connections = self.view.model.connections
        head = connections.get_connection(self.item.head)
        tail = connections.get_connection(self.item.tail)
        if not head or not tail or head.connected is tail.connected or not self.item.subject:
            self.cancel()
            return False
        self._route()
        points = [tuple(h.pos) for h in self.item.handles()]
        if len(points) < 2 or all(abs(a - b) < EPSILON for a, b in zip(points[0], points[-1])):
            self.cancel()
            return False
        self.item.horizontal = abs(points[0][1] - points[1][1]) < EPSILON
        self.item.orthogonal = True
        self.view.model.update({self.item})
        item = self.item
        tx, self.tx = self.tx, None
        tx.commit()
        self._clear()
        try:
            self.events.handle(DiagramItemPlaced(item))
        except Exception:
            # The model transaction has already succeeded; never report a
            # rollback when only a downstream UI listener failed.
            log.exception("Conexión creada; no se pudo actualizar la herramienta")
            self.events.handle(Notification("Conexión creada; no se pudo actualizar la herramienta."))
        return True

    def _key_pressed(self, _controller, keyval, keycode, _state):
        if not self.tx:
            return False
        if keyval == Gdk.KEY_Escape:
            self.cancel()
            return True
        if keyval in (Gdk.KEY_space, Gdk.KEY_Tab, Gdk.KEY_ISO_Left_Tab):
            # Use hardware code where supplied so auto-repeat cannot add points.
            key = keycode or keyval
            if key not in self.pressed:
                self.pressed.add(key)
                try:
                    if keyval == Gdk.KEY_space:
                        self.route.fix(tuple(self.item.tail.pos), tuple(self.item.head.pos))
                    else:
                        self.route.flip()
                        self._route()
                except Exception:
                    self._failure()
            return True
        # Do not let unrelated shortcuts mutate the model inside this transaction.
        return True

    def _key_released(self, _controller, keyval, keycode, _state):
        self.pressed.discard(keycode or keyval)

    def _clear(self):
        self.view.selection.grayed_out_items = set()
        self.view.selection.dropzone_item = None
        self.moving = None
        self.item = None
        self.pressed.clear()

    def cancel(self):
        if self.tx:
            tx, self.tx = self.tx, None
            try:
                tx.rollback()
            finally:
                self._clear()
                self.view.selection.unselect_all()
                for item in self.previous_selection:
                    if item.diagram:
                        self.view.selection.select_items(item)
                if self.previous_focus and self.previous_focus.diagram:
                    self.view.selection.focused_item = self.previous_focus
                self.events.handle(DiagramSelectionChanged(
                    self.view, self.view.selection.focused_item, self.view.selection.selected_items
                ))
        self.gesture.reset()

    def _cancel_gesture(self, *_args):
        if self.tx:
            self.cancel()

    def _focus_left(self, *_args):
        self.cancel()

    def _unrealize(self, *_args):
        self.close()
        self.service.drawings.discard(self)

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.cancel()
        if self.view.handler_is_connected(self.unrealize_handler):
            self.view.disconnect(self.unrealize_handler)
        for controller in (self.gesture, self.keys, self.focus):
            if controller.get_widget() is self.view:
                self.view.remove_controller(controller)


def install_drawing(page, factory, service):
    view = page.view
    for drawing in list(service.drawings):
        if drawing.view is view:
            drawing.close()
            service.drawings.discard(drawing)
    view.remove_all_controllers()
    drawing = Drawing(view, factory, page.event_manager, service)
    service.drawings.add(drawing)
    view.add_controller(view_focus_tool())
    view.add_controller(drawing.keys, drawing.gesture, drawing.focus)
    add_basic_tools(view, page.modeling_language, page.event_manager)
    return drawing
