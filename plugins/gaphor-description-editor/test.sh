#!/usr/bin/env bash
set -euo pipefail

plugin_source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
gaphor_exe=gaphor
installed=false
headless=false
installed_plugins="${GAPHOR_PLUGIN_PATH:-$HOME/.local/gaphor/plugins-2}"

usage() {
    cat <<'EOF'
Uso: bash test.sh [--installed] [--headless] [--gaphor RUTA]

--installed   Comprueba también el plugin instalado en la carpeta de Gaphor.
--headless    Usa xvfb-run; también se activa si no hay DISPLAY ni WAYLAND_DISPLAY.
--gaphor      Ejecutable nativo de Gaphor (por defecto: gaphor).
EOF
}

while (($#)); do
    case "$1" in
        --installed) installed=true; shift ;;
        --headless) headless=true; shift ;;
        --gaphor)
            if (($# < 2)) || [[ -z "$2" || "$2" == --* ]]; then
                printf 'Falta la ruta de --gaphor.\n' >&2
                exit 2
            fi
            gaphor_exe="$2"
            shift 2
            ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'Opción desconocida: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
done

for executable in "$gaphor_exe" timeout; do
    if ! command -v "$executable" >/dev/null; then
        printf 'No se encuentra el ejecutable: %s\n' "$executable" >&2
        exit 1
    fi
done

display_runner=()
if [[ "$headless" == true || ( -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ) ]]; then
    for executable in xvfb-run Xvfb xauth; do
        if ! command -v "$executable" >/dev/null; then
            printf 'Sin pantalla se necesita %s; no se instalarán dependencias automáticamente.\n' "$executable" >&2
            exit 1
        fi
    done
    display_runner=(xvfb-run -a)
    export GDK_BACKEND=x11
fi

test_output="$(mktemp -d "${TMPDIR:-/tmp}/gaphor-description-tests.XXXXXX")"
empty_plugins="$test_output/empty-plugins"
mkdir -- "$empty_plugins"
export GAPHOR_DESCRIPTION_TEST_OUTPUT="$test_output"
export PYTHONDONTWRITEBYTECODE=1
printf 'Modelos temporales y resultados: %s\n' "$test_output"

run_test() {
    local script="$1" status_name="$2" report_name="$3" plugins="$4"
    local process_log="$test_output/$script-process.txt"
    if ! GAPHOR_PLUGIN_PATH="$plugins" timeout --kill-after=5s 30s \
        "${display_runner[@]}" "$gaphor_exe" exec "$plugin_source_dir/tests/$script.py" \
        >"$process_log" 2>&1; then
        cat -- "$process_log" >&2
        printf 'Error o tiempo agotado en %s. Consulta %s.\n' "$script" "$test_output" >&2
        return 1
    fi
    if [[ -f "$test_output/$report_name" ]]; then
        cat -- "$test_output/$report_name"
    fi
    if [[ ! -f "$test_output/$status_name" ]] || [[ "$(<"$test_output/$status_name")" != PASS ]]; then
        cat -- "$process_log" >&2
        printf 'Prueba fallida: %s. Consulta %s.\n' "$script" "$test_output" >&2
        return 1
    fi
}

run_test run_in_gaphor status.txt results.txt "$empty_plugins"
run_test without_plugin without-plugin-status.txt without-plugin.txt "$empty_plugins"
if [[ "$installed" == true ]]; then
    run_test installed_plugin installed-plugin-status.txt installed-plugin.txt "$installed_plugins"
fi
printf 'Todas las comprobaciones solicitadas finalizaron correctamente.\n'
