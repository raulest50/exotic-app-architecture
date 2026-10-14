"""Independent interpreter: load, inspect and save using native Gaphor only."""

import contextlib
import logging
import os
from pathlib import Path
import sys
import traceback

from gaphor import UML
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import ElementFactory, StyleSheet
from gaphor.core.modeling.diagram import StyledItem
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.storage.load import load
from gaphor.storage.save import save
from gaphor.UML.profiles.stereotypepropertypages import stereotype_model

output = Path(os.environ["GAPHOR_DESCRIPTION_TEST_OUTPUT"])
with (output / "without-plugin.txt").open("w", encoding="utf-8") as report:
    try:
        with contextlib.redirect_stdout(report), contextlib.redirect_stderr(report):
            logging.basicConfig(stream=report, level=logging.WARNING, force=True)
            assert "gaphor_description_editor" not in sys.modules
            model = ElementFactory(EventManager())
            language = ModelingLanguageService()
            with (output / "portable.gaphor").open(encoding="utf-8") as stream:
                load(stream, model, language)
            component = next(model.select(UML.Component))
            assert component.note == "Nota independiente"
            rows = stereotype_model(component, model.event_manager)
            row = next(row for row in rows if row.name == "descripcion")
            assert row.slot_value == "Descripción portátil\nLínea 2: ñ & <texto>"
            css_row = next(row for row in rows if row.name == "css")
            assert css_row.slot_value == "color: red;"
            diagram = next(model.select(UML.Diagram))
            item = next(diagram.get_all_items())
            assert (model.style_sheet or StyleSheet()).compute_style(StyledItem(item))["color"] != (1, 0, 0, 1)
            row.slot_value = "Editado sin plugin"
            with (output / "native-resaved.gaphor").open("w", encoding="utf-8") as stream:
                save(stream, model)
            other = ElementFactory()
            with (output / "native-resaved.gaphor").open(encoding="utf-8") as stream:
                load(stream, other, language)
            loaded = other.lookup(component.id)
            assert UML.recipes.get_slot_value(loaded.appliedStereotype[0].slot[0]) == "Editado sin plugin"
            assert loaded.note == "Nota independiente"
            css_slot = next(slot for slot in loaded.appliedStereotype[0].slot if slot.definingFeature.name == "css")
            assert UML.recipes.get_slot_value(css_slot) == "color: red;"
            assert "gaphor_description_editor" not in sys.modules
            report.write("PASS: descripción, nota y CSS conservados; edición/reapertura nativa sin aplicar el CSS del plugin.\n")
            (output / "without-plugin-status.txt").write_text("PASS", encoding="utf-8")
    except Exception:
        traceback.print_exc(file=report)
        (output / "without-plugin-status.txt").write_text("FAIL", encoding="utf-8")
