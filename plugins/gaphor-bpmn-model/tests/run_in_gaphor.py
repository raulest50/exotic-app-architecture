"""Run source tests using Gaphor's own Python, GTK and model implementation."""

import contextlib
import logging
import os
from pathlib import Path
import sys
import traceback
import unittest

output = Path(os.environ["GAPHOR_BPMN_TEST_OUTPUT"])
output.mkdir(parents=True, exist_ok=True)
sys.dont_write_bytecode = True
sys.path.insert(0, os.environ.get("GAPHOR_BPMN_TEST_PACKAGE") or str(Path(__file__).resolve().parents[1]))
with (output / "results.txt").open("w", encoding="utf-8") as report:
    try:
        with contextlib.redirect_stdout(report), contextlib.redirect_stderr(report):
            logging.basicConfig(stream=report, level=logging.WARNING, force=True)
            if package := os.environ.get("GAPHOR_BPMN_TEST_PACKAGE"):
                import gaphor_bpmn_model
                from importlib.metadata import distribution
                assert Path(gaphor_bpmn_model.__file__).resolve().is_relative_to(Path(package).resolve())
                record = distribution("gaphor-bpmn-model")
                points = {point.group: point.value for point in record.entry_points}
                from gaphor_bpmn_model import __version__
                assert record.version == __version__
                assert points["gaphor.modelinglanguages"] == "gaphor_bpmn_model.language:BPMNLanguage"
                assert points["gaphor.services"] == "gaphor_bpmn_model.service:BPMNService"
                assert points["gaphor.modules"] == "gaphor_bpmn_model.service"
                print("Paquete instalado temporal y sus tres entry points comprobados:", package)
            suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent), pattern="test_*.py")
            result = unittest.TextTestRunner(stream=report, verbosity=2).run(suite)
            (output / "status.txt").write_text("PASS" if result.wasSuccessful() else "FAIL")
    except Exception:
        traceback.print_exc(file=report)
        (output / "status.txt").write_text("ERROR")
