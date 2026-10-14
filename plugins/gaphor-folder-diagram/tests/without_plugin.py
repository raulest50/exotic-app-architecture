"""Fresh process with no plugin: load, inspect, render and resave native UML."""

import contextlib
import logging
import os
from pathlib import Path
import sys
import traceback

from gaphor import UML
from gaphor.core.modeling import ElementFactory
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.storage.load import load
from gaphor.storage.save import save
from gaphor.diagram.export import save_png

output = Path(os.environ["GAPHOR_FOLDER_TEST_OUTPUT"])
with (output / "without-plugin.txt").open("w", encoding="utf-8") as report:
    try:
        with contextlib.redirect_stdout(report), contextlib.redirect_stderr(report):
            logging.basicConfig(stream=report, level=logging.WARNING, force=True)
            assert not any(name.startswith(("gaphor_folder_diagram", "gaphor_description_editor")) for name in sys.modules)
            model = ElementFactory()
            language = ModelingLanguageService()
            with (output / "portable.gaphor").open(encoding="utf-8") as stream:
                load(stream, model, language)
            diagrams = list(model.select(UML.ComponentDiagram))
            assert len(diagrams) == 1
            assert len(list(model.select(UML.Artifact))) == 5
            assert len(list(model.select(UML.Package))) == 4
            diagram = diagrams[0]
            for item in diagram.get_all_items():
                if item.parent:
                    assert item.subject.owner is item.parent.subject
            artifact = next(model.select(UML.Artifact))
            artifact.note = "Nota editable sin ningún plugin"
            save_png(str(output / "without-plugin.png"), diagram)
            with (output / "native-resaved.gaphor").open("w", encoding="utf-8") as stream:
                save(stream, model)
            other = ElementFactory()
            with (output / "native-resaved.gaphor").open(encoding="utf-8") as stream:
                load(stream, other, language)
            assert other.lookup(artifact.id).note == artifact.note
            assert len(list(other.lookup(diagram.id).get_all_items())) == 7
            report.write("PASS: modelo, jerarquía, dibujo y edición nativa conservados sin plugins.\n")
            (output / "without-plugin-status.txt").write_text("PASS", encoding="utf-8")
    except Exception:
        traceback.print_exc(file=report)
        (output / "without-plugin-status.txt").write_text("FAIL", encoding="utf-8")
