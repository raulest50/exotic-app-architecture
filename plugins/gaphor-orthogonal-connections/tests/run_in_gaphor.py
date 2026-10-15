import contextlib
import logging
import os
from pathlib import Path
import sys
import traceback
import unittest

output = Path(os.environ["GAPHOR_ORTHOGONAL_TEST_OUTPUT"])
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
with (output / "results.txt").open("w", encoding="utf-8") as report:
    try:
        with contextlib.redirect_stdout(report), contextlib.redirect_stderr(report):
            logging.basicConfig(stream=report, level=logging.WARNING, force=True)
            suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent), pattern="test_*.py")
            result = unittest.TextTestRunner(stream=report, verbosity=2).run(suite)
            (output / "status.txt").write_text("PASS" if result.wasSuccessful() else "FAIL", encoding="utf-8")
    except Exception:
        traceback.print_exc(file=report)
        (output / "status.txt").write_text("ERROR", encoding="utf-8")
