#!/usr/bin/env bash
set -euo pipefail

plugin_source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python_exe=python3
plugin_directory="${GAPHOR_PLUGIN_PATH:-$HOME/.local/gaphor/plugins-2}"

usage() {
    cat <<'EOF'
Uso: bash install.sh [--python RUTA] [--plugin-directory RUTA]

Instala el plugin para Gaphor 3.3.2 nativo de Linux, sin descargar dependencias.
--python             Python de Gaphor (por defecto: python3).
--plugin-directory   Destino (GAPHOR_PLUGIN_PATH o ~/.local/gaphor/plugins-2).
EOF
}

while (($#)); do
    case "$1" in
        --python|--plugin-directory)
            if (($# < 2)) || [[ -z "$2" || "$2" == --* ]]; then
                printf 'Falta el valor de %s.\n' "$1" >&2
                exit 2
            fi
            if [[ "$1" == --python ]]; then
                python_exe="$2"
            else
                plugin_directory="$2"
            fi
            shift 2
            ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'Opción desconocida: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
done

"$python_exe" - <<'PY'
import sys
from importlib.metadata import PackageNotFoundError, version

if sys.version_info < (3, 12):
    sys.exit("Se necesita Python 3.12 o posterior.")
try:
    installed = {name: version(name) for name in ("gaphor", "pip", "setuptools", "wheel")}
except PackageNotFoundError as error:
    sys.exit(f"Falta {error.name} en este Python. Usa el intérprete de Gaphor con --python.")
if installed["gaphor"] != "3.3.2":
    sys.exit(f"Se necesita Gaphor 3.3.2; se encontró {installed['gaphor']}.")
if int(installed["setuptools"].split(".")[0]) < 68:
    sys.exit("Se necesita setuptools >= 68.")
print(f"Python {sys.version.split()[0]}; Gaphor {installed['gaphor']}. Dependencias disponibles.")
PY

# Empaquetar una copia temporal evita generar build/ o metadatos en las fuentes.
install_source_dir="$(mktemp -d "${TMPDIR:-/tmp}/gaphor-description-install.XXXXXX")"
trap 'rm -rf -- "$install_source_dir"' EXIT
cp -- "$plugin_source_dir/pyproject.toml" "$install_source_dir/"
cp -R -- "$plugin_source_dir/gaphor_description_editor" "$install_source_dir/"

"$python_exe" -m pip install \
    --no-index --no-deps --no-build-isolation --no-compile \
    --disable-pip-version-check --no-cache-dir --upgrade \
    --target "$plugin_directory" "$install_source_dir"

printf 'Plugin instalado en %s. Reinicia Gaphor para cargarlo.\n' "$plugin_directory"
