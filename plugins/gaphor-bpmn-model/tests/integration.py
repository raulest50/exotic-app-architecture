"""Real session/service integration with temporary models and native rendering."""

import asyncio
import contextlib
import io
import logging
import os
from pathlib import Path
import sys
import traceback
from unittest.mock import patch

sys.dont_write_bytecode = True
root_directory = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.environ.get("GAPHOR_BPMN_TEST_PACKAGE") or str(root_directory))
for directory in ("gaphor-description-editor", "gaphor-folder-diagram", "gaphor-copy-reference", "gaphor-postgres-model"):
    sys.path.insert(0, str(root_directory.parent / directory))
output = Path(os.environ["GAPHOR_BPMN_TEST_OUTPUT"])


def menu_labels(menu):
    from gi.repository import Gio
    for index in range(menu.get_n_items()):
        title = menu.get_item_attribute_value(index, "label", None)
        if title:
            yield title.get_string()
        for kind in (Gio.MENU_LINK_SECTION, Gio.MENU_LINK_SUBMENU):
            child = menu.get_item_link(index, kind)
            if child:
                yield from menu_labels(child)


def example(session):
    from gaphor.core import Transaction
    from gaphor.core.modeling import StyleSheet
    from gaphor_bpmn_model import model as m
    from gaphor_bpmn_model import diagram as d
    from gaphor_bpmn_model.operations import create_participant, create_lane, create_node, create_flow

    events = session.get_service("event_manager")
    factory = session.get_service("element_factory")
    service = session.get_service("bpmn_model")
    diagram = service.new_diagram()
    root = diagram.element
    with Transaction(events):
        sheet = factory.style_sheet or factory.create(StyleSheet)
        sheet.styleSheet = "diagram { background-color: white; color: #172129; }"
    client = create_participant(root, events, "Cliente", is_closed=True)
    exotic = create_participant(root, events, "Exotic")
    attention = create_lane(exotic.processRef, events, "Atención")
    warehouse = create_lane(exotic.processRef, events, "Bodega")
    def node(cls, title, lane=attention, **attrs):
        return create_node(cls, exotic.processRef, events, name=title, lane=lane, **attrs)
    start = node(m.BPMNEvent, "Pedido recibido", eventDefinition="MESSAGE")
    validate = node(m.BPMNTask, "Validar pedido")
    decision = node(m.BPMNGateway, "¿Pedido completo?")
    prepare = node(m.BPMNSubProcess, "Preparar pedido", lane=warehouse)
    notify = node(m.BPMNTask, "Notificar despacho")
    end = node(m.BPMNEvent, "Pedido atendido", eventKind="END", eventDirection="THROW")
    correction = node(m.BPMNTask, "Solicitar corrección")
    received = node(m.BPMNEvent, "Corrección recibida", eventKind="INTERMEDIATE", eventDefinition="MESSAGE", eventDirection="CATCH")
    annotation = create_node(m.BPMNTextAnnotation, root, events, name="Criterio",
                             text="Verificar dirección\ny disponibilidad.")
    relations = []
    def sequence(source, target, **attrs):
        value = create_flow(m.BPMNSequenceFlow, source, target, events, **attrs)
        relations.append(value)
        return value
    sequence(start, validate)
    sequence(validate, decision)
    sequence(decision, prepare, name="Completo", flowKind="CONDITIONAL", conditionExpression="Pedido completo")
    sequence(prepare, notify)
    sequence(notify, end)
    sequence(decision, correction, name="Corregir", flowKind="DEFAULT")
    sequence(correction, received)
    sequence(received, validate)
    relations.extend((create_flow(m.BPMNMessageFlow, client, start, events, name="Pedido"),
                      create_flow(m.BPMNMessageFlow, correction, client, events, name="Solicitud"),
                      create_flow(m.BPMNMessageFlow, client, received, events, name="Corrección"),
                      create_flow(m.BPMNAssociation, validate, annotation, events)))
    layouts = (
        (client, d.BPMNParticipantItem, 20, 20, 1300, 90),
        (exotic, d.BPMNParticipantItem, 20, 200, 1300, 620),
        (attention, d.BPMNLaneItem, 55, 200, 1265, 390),
        (warehouse, d.BPMNLaneItem, 55, 590, 1265, 230),
        (start, d.BPMNEventItem, 110, 280, 44, 44),
        (validate, d.BPMNTaskItem, 250, 265, 170, 78),
        (decision, d.BPMNGatewayItem, 490, 277, 54, 54),
        (prepare, d.BPMNSubProcessItem, 680, 660, 175, 80),
        (notify, d.BPMNTaskItem, 960, 265, 170, 78),
        (end, d.BPMNEventItem, 1210, 280, 44, 44),
        (correction, d.BPMNTaskItem, 680, 445, 175, 80),
        (received, d.BPMNEventItem, 490, 462, 44, 44),
        (annotation, d.BPMNTextAnnotationItem, 230, 395, 190, 88),
    )
    figures = {}
    with Transaction(events):
        for value, cls, x, y, width, height in layouts:
            item = diagram.create(cls, subject=value)
            item.matrix.translate(x, y)
            item.width, item.height = width, height
            figures[value] = item
        for relation in relations:
            assert d.drop_flow(relation, diagram) is not None
    return diagram, exotic, validate, figures


async def verify(sessions):
    from gi.repository import Gtk
    from gaphor.core import Transaction
    from gaphor.core.modeling import ElementFactory
    from gaphor.diagram.export import save_png, save_svg
    from gaphor.storage.save import save
    from gaphor.storage.load import load
    from gaphor.ui.actiongroup import window_action_group
    from gaphor_bpmn_model import model as m
    from gaphor_bpmn_model.operations import snapshot
    from gaphor_bpmn_model.validation import validate

    opened = []
    async_errors = []
    asyncio.get_running_loop().set_exception_handler(lambda _loop, error: async_errors.append(error))
    try:
        for index, session in enumerate(sessions):
            events = session.get_service("event_manager")
            factory = session.get_service("element_factory")
            language = session.get_service("modeling_language")
            diagrams = session.get_service("diagrams")
            window = Gtk.Window(default_width=1100, default_height=750)
            session.get_service("main_window").window = window
            window.set_child(diagrams.open())
            window.insert_action_group("win", window_action_group(session.component_registry))
            opened.append((diagrams, window))
            language.select_modeling_language("BPMN")
            assert language.name == "BPMN"
            service = session.get_service("bpmn_model")
            assert service.compatible
            for other in ("description_editor", "folder_diagram", "copy_reference", "postgres_model"):
                assert session.get_service(other).compatible, other
            diagram, pool, task, figures = example(session)
            await asyncio.sleep(0.1)
            errors = [issue for issue in validate(diagram.element, final=True) if issue.severity == "error"]
            assert not errors, errors
            labels = list(menu_labels(session.get_service("tools_menu").menu))
            assert labels.count("Custom tools") == 1, labels
            assert "BPMN" in labels and "Modelo relacional" in labels
            # Both property editors operate on the same custom NamedElement.
            from gaphor_description_editor.model import read_description, save_properties
            save_properties(task, "Revisión del pedido", "Nota del proceso", "", events)
            assert read_description(task) == "Revisión del pedido"
            editor = service.open_editor(task)
            editor.documentation.get_buffer().set_text("Validar antes de preparar")
            assert editor.save(), editor.error.get_text()
            assert task.documentation == "Validar antes de preparar"
            assert read_description(task) == "Revisión del pedido"
            with patch.object(service, "_show_report"):
                assert service.validate_diagram() is not None
            with Transaction(events):
                save_png(str(output / f"bpmn-ejemplo-{index}.png"), diagram)
                save_svg(str(output / f"bpmn-ejemplo-{index}.svg"), diagram)
            saved = io.StringIO()
            save(saved, factory)
            (output / f"bpmn-ejemplo-{index}.gaphor").write_text(saved.getvalue(), encoding="utf-8")
            restored = ElementFactory()
            load(io.StringIO(saved.getvalue()), restored, language)
            assert snapshot(restored.lookup(task.id)) == snapshot(task)
            assert len(list(restored.select(m.BPMNMessageFlow))) == 3
            assert restored.lookup(pool.id).processRef is not None
            restored.shutdown()
            # The namespace must not silently resolve to UML without the plugin.
            bpmn_language = language._modeling_languages.pop("BPMN")
            try:
                try:
                    language.lookup_element("BPMNTask", "BPMN")
                except ValueError:
                    pass
                else:
                    raise AssertionError("El namespace BPMN no debe resolverse sin su lenguaje")
            finally:
                language._modeling_languages["BPMN"] = bpmn_language
            print(f"Sesión {index}: coexistencia, propiedades, validación, guardado/reapertura y PNG/SVG OK")
        a, b = (session.get_service("bpmn_model") for session in sessions)
        a.shutdown()
        before = sessions[1].get_service("element_factory").size()
        assert b.new_diagram() is not None
        assert sessions[1].get_service("element_factory").size() > before
        assert not async_errors, async_errors
        print("Dos sesiones independientes y cierre del servicio OK")
    finally:
        for diagrams, window in opened:
            for diagram in list(diagrams.element_factory.select(m.BPMNDiagram)):
                diagrams.close_diagram_page(diagram)
            diagrams.close()
            window.set_child(None)
            window.destroy()
        await asyncio.sleep(0.05)


with (output / "integration.txt").open("w", encoding="utf-8") as report:
    try:
        with contextlib.redirect_stdout(report), contextlib.redirect_stderr(report):
            logging.basicConfig(stream=report, level=logging.WARNING, force=True)
            from gi.repository import Gtk
            import gi.events
            from gaphor.application import Session
            from gaphor.entrypoint import load_entry_points
            from gaphor.services.properties import Properties
            from gaphor_bpmn_model.language import BPMNLanguage
            from gaphor_bpmn_model.service import BPMNService
            from gaphor_description_editor import DescriptionEditor
            from gaphor_folder_diagram import FolderDiagramService
            from gaphor_copy_reference import CopyReferenceService
            from gaphor_postgres_model.service import PostgresService
            from gaphor_postgres_model.language import PostgreSQLLanguage
            services = dict(load_entry_points("gaphor.services"))
            languages = dict(load_entry_points("gaphor.modelinglanguages"))
            services.update(bpmn_model=BPMNService, description_editor=DescriptionEditor,
                            folder_diagram=FolderDiagramService, copy_reference=CopyReferenceService,
                            postgres_model=PostgresService)
            languages["BPMN"] = BPMNLanguage
            languages["PostgreSQL"] = PostgreSQLLanguage
            def source_entries(scope, names=None):
                if scope == "gaphor.services":
                    return dict(services)
                if scope == "gaphor.modelinglanguages":
                    return dict(languages)
                return load_entry_points(scope, names)
            Gtk.init()
            with patch("gaphor.entrypoint.load_entry_points", side_effect=source_entries), \
                 patch.object(Gtk.Window, "present"), patch.object(Properties, "save"), \
                 gi.events.GLibEventLoopPolicy():
                sessions = (Session(), Session())
                try:
                    asyncio.get_event_loop().run_until_complete(verify(sessions))
                finally:
                    for session in sessions:
                        session.shutdown()
            print("PASS: integración BPMN con los cuatro plugins existentes; perfil y modelos del usuario sin editar.")
        (output / "integration-status.txt").write_text("PASS", encoding="utf-8")
    except Exception:
        traceback.print_exc(file=report)
        (output / "integration-status.txt").write_text("FAIL", encoding="utf-8")
