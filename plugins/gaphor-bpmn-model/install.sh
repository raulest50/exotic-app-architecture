#!/usr/bin/env bash
set -euo pipefail
python_exe="${PYTHON:-python3}"
plugin_dir="${GAPHOR_PLUGIN_PATH:-$HOME/.local/gaphor/plugins-2}"
while (($#)); do
  case "$1" in
    --python) python_exe="$2"; shift 2 ;;
    --target) plugin_dir="$2"; shift 2 ;;
    *) echo "Opción desconocida: $1" >&2; exit 2 ;;
  esac
done
"$python_exe" -c 'import importlib.metadata as m; import sys; assert sys.version_info >= (3, 12); assert m.version("gaphor") == "3.3.2", "Se necesita Gaphor 3.3.2 en el intérprete elegido"'
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
"$python_exe" -m pip install --no-index --no-deps --no-build-isolation --no-compile --upgrade --target "$plugin_dir" "$script_dir"
"$python_exe" - "$plugin_dir" <<'PY'
from importlib.metadata import PathDistribution
from pathlib import Path
import shutil
import sys

root = Path(sys.argv[1]).resolve(strict=True)
matches = list(root.glob("gaphor_bpmn_model-*.dist-info"))
current = root / "gaphor_bpmn_model-0.1.0.dist-info"
assert current.is_dir(), "No se encontraron los metadatos instalados"
for path in matches:
    if path == current:
        continue
    assert not path.is_symlink() and path.resolve().parent == root
    assert PathDistribution(path).metadata["Name"] == "gaphor-bpmn-model"
    shutil.rmtree(path)
PY
echo "Plugin instalado en $plugin_dir. Reinicia Gaphor y selecciona BPMN."
