"""Fresh Gaphor process without any custom plugin on its import path."""
import json
import os
from pathlib import Path
import sys
import traceback

from gaphor.core.modeling import ElementFactory
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.storage.load import load
from gaphor.storage.save import save

output = Path(os.environ["GAPHOR_ORTHOGONAL_TEST_OUTPUT"])
with (output / "without-plugin-results.txt").open("w", encoding="utf-8") as report:
    try:
        assert not any(n.startswith("gaphor_orthogonal_connections") for n in sys.modules)
        model = ElementFactory()
        language = ModelingLanguageService()
        with (output / "portable.gaphor").open(encoding="utf-8") as stream:
            load(stream, model, language)
        expected = json.loads((output / "geometry.json").read_text(encoding="utf-8"))
        for item_id, positions in expected.items():
            item = model.lookup(item_id)
            item.diagram.update(item.diagram.get_all_items())
            assert [list(map(float, h.pos)) for h in item.handles()] == positions
            assert item.subject.client and item.subject.supplier
        with (output / "native-resaved.gaphor").open("w", encoding="utf-8") as stream:
            save(stream, model)
        assert not any(n.startswith("gaphor_orthogonal_connections") for n in sys.modules)
        report.write("PASS: conexiones y coordenadas nativas conservadas sin plugins.\n")
        (output / "without-plugin-status.txt").write_text("PASS", encoding="utf-8")
    except Exception:
        traceback.print_exc(file=report)
        (output / "without-plugin-status.txt").write_text("FAIL", encoding="utf-8")
