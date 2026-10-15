"""Interactive disposable canvas. No user model or persistent settings are used.

Run with `gaphor exec <this file>`. Optional GAPHOR_ORTHOGONAL_UI_KEY_TEST=1
injects GTK Space/Tab signals during a real mouse drag for automation tools
which cannot hold a mouse button while sending keyboard input.
"""
import asyncio
import json
import logging
import os
from pathlib import Path
import sys
import tempfile
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gi.repository import Gdk, Gio, GLib, Gtk
from gaphor import UML
from gaphor.core import Transaction
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import ElementFactory, StyleSheet
from gaphor.core.modeling.elementdispatcher import ElementDispatcher
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.services.undomanager import UndoManager
from gaphor.UML.classes.component import ComponentItem
from gaphor.UML.classes.dependency import DependencyItem
from gaphor.UML.deployments.artifact import ArtifactItem
from gaphor.ui.actiongroup import apply_action_group
from gaphor.ui.diagrampage import DiagramPage
from gaphor.ui.menufragment import MenuFragment
from gaphor_orthogonal_connections import OrthogonalConnections

output = Path(os.environ.get("GAPHOR_ORTHOGONAL_TEST_OUTPUT") or tempfile.mkdtemp(prefix="gaphor-orthogonal-ui-"))
output.mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=str(output / "ui.log"), level=logging.INFO, force=True)


async def main():
    Gtk.init()
    events = EventManager()
    language = ModelingLanguageService(events)
    dispatcher = ElementDispatcher(events, language)
    model = ElementFactory(events, dispatcher)
    undo = UndoManager(events, model)
    menu = MenuFragment()
    service = OrthogonalConnections(menu, events)
    with Transaction(events):
        sheet = model.create(StyleSheet)
        sheet.styleSheet = "diagram { background-color: white; } * { color: black; background-color: white; line-width: 1; font-size: 14; }"
        diagram = model.create(UML.ComponentDiagram)
        diagram.name = "Prueba temporal"
        source = diagram.create(ArtifactItem, subject=model.create(UML.Artifact))
        source.subject.name = "Origen.tsx"
        source.width, source.height = 180, 100
        source.matrix.translate(80, 80)
        target = diagram.create(ComponentItem, subject=model.create(UML.Component))
        target.subject.name = "Destino"
        target.width, target.height = 180, 100
        target.matrix.translate(650, 350)
    page = DiagramPage(diagram, events, model, language)
    widget = page.construct()
    widget.set_vexpand(True)
    window = Gtk.Window(title="Prueba temporal — Conexiones ortogonales")
    window.set_default_size(1000, 700)
    layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    bar = Gtk.Box(spacing=10)
    tools = Gtk.MenuButton(label="Tools", menu_model=menu.menu)
    bar.append(tools)
    select = Gtk.Button(label="Dependencia (Shift+D)")
    bar.append(select)
    back = Gtk.Button(label="Deshacer")
    back.connect("clicked", lambda *_: undo.undo_transaction())
    bar.append(back)
    forward = Gtk.Button(label="Rehacer")
    forward.connect("clicked", lambda *_: undo.redo_transaction())
    bar.append(forward)
    layout.append(bar)
    label = Gtk.Label(label="Activa Tools → Custom tools → Conexiones ortogonales. Arrastra Origen → Destino.")
    layout.append(label)
    layout.append(widget)
    window.set_child(layout)
    apply_action_group(service, "win", window)
    running = True
    key_records = []
    armed = False

    def arm(*_):
        nonlocal armed
        page.select_tool("toolbox-dependency")
        armed = False
        for drawing in list(service.drawings):
            def record(_gesture, dx, dy, drawing=drawing):
                nonlocal armed
                if drawing.tx and not armed and abs(dx) > 80 and os.environ.get("GAPHOR_ORTHOGONAL_UI_KEY_TEST"):
                    armed = True
                    before = len(drawing.route.legs)
                    for key, code in ((Gdk.KEY_space, 32), (Gdk.KEY_Tab, 9)):
                        drawing.keys.emit("key-pressed", key, code, Gdk.ModifierType(0))
                        drawing.keys.emit("key-released", key, code, Gdk.ModifierType(0))
                    key_records.append({"real_drag": True, "keys": "GTK Space/Tab signals",
                                        "before": before, "after": len(drawing.route.legs),
                                        "transaction_alive": drawing.tx is not None})
            drawing.gesture.connect_after("drag-update", record)
    select.connect("clicked", arm)

    def close(*_):
        nonlocal running
        running = False
        return True
    window.connect("close-request", close)
    for item in (source, target):
        item.update_shapes()
    diagram.update(diagram.get_all_items())
    window.present()
    try:
        while running:
            while GLib.MainContext.default().pending():
                GLib.MainContext.default().iteration(False)
            lines = [item for item in diagram.get_all_items() if isinstance(item, DependencyItem)]
            status = {"enabled": service.enabled, "transaction": Transaction.in_transaction(),
                      "matrix": tuple(page.view.matrix), "size": (page.view.get_width(), page.view.get_height()),
                      "items": [(i.subject.name if i.subject else None, tuple(i.matrix_i2c)) for i in diagram.get_all_items()],
                      "keys": key_records, "lines": [{"id": item.id,
                      "points": [list(map(float, h.pos)) for h in item.handles()],
                      "orthogonal": bool(item.orthogonal),
                      "client": [e.name for e in item.subject.client] if item.subject else [],
                      "supplier": [e.name for e in item.subject.supplier] if item.subject else []}
                      for item in lines]}
            (output / "ui-state.json").write_text(json.dumps(status), encoding="utf-8")
            await asyncio.sleep(0.05)
    finally:
        service.shutdown()
        page.close()
        window.destroy()
        undo.shutdown()
        model.shutdown()
        dispatcher.shutdown()
        language.shutdown()

try:
    asyncio.run(main())
except Exception:
    (output / "ui-error.txt").write_text(traceback.format_exc(), encoding="utf-8")
    raise
