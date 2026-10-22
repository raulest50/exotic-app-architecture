"""Exercise the real Gaphor session/UI stack and all four installed services."""
import asyncio
import contextlib
import io
import logging
import os
from pathlib import Path
import sys
import traceback
import faulthandler
from types import SimpleNamespace
from unittest.mock import patch

installed = globals().get("INSTALLED", False)
plugins = Path(__file__).resolve().parents[2]
if not installed:
    for directory in ("gaphor-postgres-model", "gaphor-description-editor", "gaphor-folder-diagram", "gaphor-copy-reference"):
        sys.path.insert(0, str(plugins / directory))
sys.path.insert(0, str(plugins / "gaphor-copy-reference" / "tests"))
output = Path(os.environ["GAPHOR_POSTGRES_TEST_OUTPUT"])
prefix = "installed-plugin" if installed else "integration"


async def settle():
    # The test uses Gaphor's GLibEventLoopPolicy. Re-entering context.iteration
    # from an async callback can invalidate pending native clipboard requests.
    await asyncio.sleep(0.08)


async def verify(sessions):
    from gi.repository import Gtk, Gdk, Gsk, GLib
    from gaphas.tool.zoom import on_scroll
    from gaphor import UML
    from gaphor.core import Transaction
    from gaphor.core.modeling import ElementFactory, StyleSheet
    from gaphor.core.modeling.diagram import StyledItem
    from gaphor.core.styling import PrefersColorScheme
    from gaphor.diagram.event import DiagramOpened, DiagramItemPlaced, DiagramSelectionChanged
    from gaphor.diagram.presentation import connect
    from gaphor.diagram.export import save_png, save_svg
    from gaphor.diagram.tools import textedit
    from gaphor.storage.save import save
    from gaphor.storage.load import load
    from gaphor.ui.actiongroup import window_action_group
    from gaphor.ui.clipboard import Clipboard
    from gaphor.ui import modelbrowser
    from gaphor_postgres_model.model import PGTable, PGKey, PGForeignKey, PGSchema, columns, rules
    from gaphor_postgres_model.operations import snapshot, new_column, new_key, save_table
    from gaphor_postgres_model.language import relational_tools
    from gaphor_postgres_model.diagram import PGForeignKeyItem, drop_fk
    from gaphor_description_editor.model import read_description, read_css, save_properties
    from helpers import entries, action_target

    errors, opened, captured = [], [], []
    asyncio.get_running_loop().set_exception_handler(lambda _loop, error: errors.append(error))
    try:
        with patch("sys.excepthook", side_effect=lambda *error: errors.append(error)):
            for number, session in enumerate(sessions):
                events, model = session.get_service("event_manager"), session.get_service("element_factory")
                service = session.get_service("postgres_model")
                language = session.get_service("modeling_language")
                diagrams, undo = session.get_service("diagrams"), session.get_service("undo_manager")
                properties = session.get_service("description_editor")
                importer, copier = session.get_service("folder_diagram"), session.get_service("copy_reference")
                assert service.compatible and properties.compatible and importer.compatible and copier.compatible
                window = Gtk.Window(default_width=1000, default_height=700)
                session.get_service("main_window").window = window
                window.set_child(diagrams.open())
                window.insert_action_group("win", window_action_group(session.component_registry))
                window.present()
                opened.append((diagrams, window))
                language.select_modeling_language("PostgreSQL")
                assert language.name == "PostgreSQL"
                assert any(d.name == "Diagrama relacional" for d in language.diagram_types)
                diagram = service.new_diagram()
                await settle()
                with Transaction(events):
                    sheet = model.style_sheet or model.create(StyleSheet)
                    sheet.styleSheet = "diagram { background-color: white; color: black; }"
                    schema_item = relational_tools.tools[0].item_factory(diagram)
                    schema_item.width, schema_item.height = 950, 500
                    a = relational_tools.tools[1].item_factory(diagram, schema_item)
                    b = relational_tools.tools[1].item_factory(diagram, schema_item)
                    a.matrix.translate(50, 90); b.matrix.translate(520, 90)
                parent, child = a.subject, b.subject
                for table, name in ((parent, "productos"), (child, "lotes")):
                    data = snapshot(table); data["name"] = name
                    col = new_column(); col.update(name="id", type="bigint", identity="BY DEFAULT")
                    key = new_key(); key.update(name=name + "_pk", kind="PRIMARY", columns=[col["id"]])
                    data["columns"] = [col]; data["keys"] = [key]
                    if table is child:
                        ref = new_column(); ref.update(name="producto_id", type="bigint")
                        data["columns"].append(ref)
                    save_table(table, data, events)
                await settle()
                # Real placement event: cancelled drafts never create an incomplete FK.
                with Transaction(events):
                    preview = relational_tools.tools[2].item_factory(diagram)
                    connect(preview, preview.tail, b); connect(preview, preview.head, a)
                    events.handle(DiagramItemPlaced(preview))
                await settle()
                assert service.window and service.window.child
                assert model.lookup(preview.id) is None and not rules(child, PGForeignKey)
                service.window.cancel()
                with Transaction(events):
                    preview = relational_tools.tools[2].item_factory(diagram)
                    connect(preview, preview.tail, b); connect(preview, preview.head, a)
                    events.handle(DiagramItemPlaced(preview))
                await settle()
                editor = service.window; form = editor.child
                form.pairs.add()
                form.pairs.controls[0][2].set_active_id(columns(child)[1].id)
                form.pairs.controls[0][3].set_active_id(columns(parent)[0].id)
                assert form.save()
                undo.clear_undo_stack()
                assert editor.save()
                await settle()
                assert len(rules(child, PGForeignKey)) == 1
                assert any(isinstance(i, PGForeignKeyItem) for i in diagram.get_all_items())
                undo.undo_transaction(); await settle()
                assert not rules(child, PGForeignKey)
                undo.redo_transaction(); await settle()
                assert len(rules(child, PGForeignKey)) == 1
                assert not service.validate_database()
                # Existing Properties keeps double-click, description, note and CSS.
                view = diagrams.get_current_view()
                assert textedit.instant_editor(a, view, events, (10, 10))
                assert properties.editor.subject is parent
                properties.editor.cancel()
                save_properties(parent, "Descripción relacional", "Nota independiente", "color: navy; background-color: lightblue;", events)
                await settle()
                assert read_description(parent) == "Descripción relacional"
                assert parent.note == "Nota independiente" and "lightblue" in read_css(parent)
                style = (model.style_sheet or StyleSheet()).compute_style(StyledItem(a))
                assert style["color"] == (0, 0, 0.5019607843137255, 1)
                # Ctrl+wheel emits the real empty/selected selection events as before.
                controller = SimpleNamespace(get_widget=lambda: view,
                    get_current_event_state=lambda: Gdk.ModifierType.CONTROL_MASK, get_current_event=lambda: None)
                assert on_scroll(controller, 0, -1)
                events.handle(DiagramSelectionChanged(view, None, set()))
                events.handle(DiagramSelectionChanged(view, b, {b}))
                assert service.focused is b
                await settle()
                menu = modelbrowser.popup_model(parent, language)
                target = action_target(menu, "Copiar nombre")
                assert copier._copy(target, False)
                assert await window.get_clipboard().read_text_async() == "productos"
                await settle()
                labels = [entry[0] for entry in entries(session.get_service("tools_menu").menu)]
                assert labels.count("Custom tools") == 1
                assert "Modelo relacional" in labels and "Propiedades…" in labels
                assert "Importar/leer componente en crudo…" in labels
                # Native GTK clipboard, including native deep paste and undo.
                print(f"Session {number}: native clipboard copy", flush=True)
                clipboard = Clipboard(events, model, window.get_clipboard())
                view.selection.unselect_all(); view.selection.select_items(a, b)
                with Transaction(events): clipboard.copy(view)
                assert clipboard.can_paste()
                print(f"Session {number}: native clipboard paste", flush=True)
                before_ids = {t.id for t in model.select(PGTable)}
                clipboard.paste_full(view)
                for _ in range(30):
                    await settle()
                    if clipboard._background_task is None: break
                await asyncio.wait_for(clipboard.gather_background_task(), 2)
                print(f"Session {number}: native clipboard completed", flush=True)
                cloned = [t for t in model.select(PGTable) if t.id not in before_ids]
                assert len(cloned) == 2
                copied_fk = next(r for t in cloned for r in rules(t, PGForeignKey))
                assert copied_fk.targetTable in cloned
                undo.undo_transaction(); await settle()
                assert {t.id for t in model.select(PGTable)} == before_ids
                captured.append((clipboard, view, b, model, events))
                # Native renderer and storage: all custom types, documentation and FKs.
                with Transaction(events):
                    save_png(str(output / f"{prefix}-{number}.png"), diagram)
                    save_svg(str(output / f"{prefix}-{number}.svg"), diagram)
                    sheet.styleSheet = "diagram { background-color: #242424; }"
                    assert sheet.compute_style(StyledItem(b), PrefersColorScheme.DARK)["color"] == (1, 1, 1, 1)
                    original_compute = sheet.compute_style
                    with patch.object(sheet, "compute_style", side_effect=lambda node, *args: original_compute(node, PrefersColorScheme.DARK)):
                        save_png(str(output / f"{prefix}-{number}-dark.png"), diagram)
                    sheet.styleSheet = "diagram { background-color: white; color: black; }"
                xml = io.StringIO(); save(xml, model)
                (output / f"{prefix}-{number}.gaphor").write_text(xml.getvalue(), encoding="utf-8")
                restored = ElementFactory()
                load(io.StringIO(xml.getvalue()), restored, language)
                assert snapshot(restored.lookup(child.id)) == snapshot(child)
                assert read_description(restored.lookup(parent.id)) == "Descripción relacional"
                restored.shutdown()
                # Opening a second representation never creates another table.
                second_diagram = service.new_diagram()
                with Transaction(events):
                    from gaphor.diagram.drop import drop
                    second_figure = drop(parent, second_diagram, 40, 40)
                assert second_figure.subject is parent
                events.handle(DiagramOpened(diagram)); await settle()
                if number == 0:
                    editor = service.open_table(child)
                    await settle()
                    # Capture the actual native GTK dialog for visual inspection.
                    paintable = Gtk.WidgetPaintable.new(editor)
                    snap = Gtk.Snapshot()
                    paintable.snapshot(snap, editor.get_width(), editor.get_height())
                    node = snap.to_node()
                    if node:
                        renderer = Gsk.Renderer.new_for_surface(editor.get_surface())
                        renderer.render_texture(node, None).save_to_png(str(output / "table-editor.png"))
                        renderer.unrealize()
                    editor.cancel()
                assert not errors, errors
            first, second = sessions
            clipboard, view, child_figure, _, first_events = captured[0]
            view.selection.unselect_all(); view.selection.select_items(child_figure)
            with Transaction(first_events): clipboard.copy(view)
            receiver, target_view, _, target_model, _ = captured[1]
            before = target_model.size()
            receiver.paste_full(target_view)
            for _ in range(30):
                await settle()
                if receiver._background_task is None: break
            await asyncio.wait_for(receiver.gather_background_task(), 2)
            assert target_model.size() == before, "Missing cross-project references were not rolled back"
            assert first.get_service("element_factory") is not second.get_service("element_factory")
            before = second.get_service("element_factory").size()
            first.get_service("postgres_model").shutdown()
            second.get_service("postgres_model").new_diagram()
            assert second.get_service("element_factory").size() > before
            assert not errors, errors
    finally:
        for diagrams, window in opened:
            for diagram in list(diagrams.element_factory.select(UML.Diagram)):
                diagrams.close_diagram_page(diagram)
            diagrams.close(); window.set_child(None); window.destroy()
        await settle()


with (output / f"{prefix}.txt").open("w", encoding="utf-8") as report:
    try:
        faulthandler.enable(file=report)
        with contextlib.redirect_stdout(report), contextlib.redirect_stderr(report):
            logging.basicConfig(stream=report, level=logging.WARNING, force=True)
            from gi.repository import Gtk
            import gi.events
            from gaphor.application import Session
            from gaphor.entrypoint import load_entry_points
            from gaphor.ui.clipboard import Clipboard
            from gaphor_postgres_model.service import PostgresService
            from gaphor_postgres_model.language import PostgreSQLLanguage
            from gaphor_description_editor import DescriptionEditor
            from gaphor_folder_diagram import FolderDiagramService
            from gaphor_copy_reference import CopyReferenceService
            if installed:
                from importlib.metadata import distributions
                records = list(distributions())
                for name, version in (("gaphor-postgres-model", "0.1.0"), ("gaphor-description-editor", "0.3.0"),
                                      ("gaphor-folder-diagram", "0.1.1"), ("gaphor-copy-reference", "0.1.0")):
                    matches = [d for d in records if d.metadata["Name"] == name]
                    assert len(matches) == 1 and matches[0].version == version, (name, matches)
            services = dict(load_entry_points("gaphor.services"))
            languages = dict(load_entry_points("gaphor.modelinglanguages"))
            services.update(postgres_model=PostgresService, description_editor=DescriptionEditor,
                            folder_diagram=FolderDiagramService, copy_reference=CopyReferenceService)
            languages["PostgreSQL"] = PostgreSQLLanguage
            def source_entries(scope, names=None):
                if scope == "gaphor.services": return dict(services)
                if scope == "gaphor.modelinglanguages": return dict(languages)
                return load_entry_points(scope, names)
            loader = contextlib.nullcontext() if installed else patch("gaphor.entrypoint.load_entry_points", side_effect=source_entries)
            Gtk.init()
            original_paste = Clipboard._paste
            original_copy = Clipboard._copy
            original_can_paste = Clipboard.can_paste
            with loader, gi.events.GLibEventLoopPolicy():
                sessions = (Session(), Session())
                try:
                    asyncio.get_event_loop().run_until_complete(verify(sessions))
                finally:
                    for session in sessions: session.shutdown()
            assert Clipboard._paste is original_paste
            assert Clipboard._copy is original_copy
            assert Clipboard.can_paste is original_can_paste
            print("PASS: lenguaje, editor GTK, FK por gesto, cancelar, undo/redo, CSS, zoom, copiar referencias, dos proyectos, guardar/reabrir y exportar.")
        (output / f"{prefix}-status.txt").write_text("PASS", encoding="utf-8")
    except Exception:
        traceback.print_exc(file=report)
        (output / f"{prefix}-status.txt").write_text("FAIL", encoding="utf-8")
