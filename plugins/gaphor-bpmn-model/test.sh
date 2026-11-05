#!/usr/bin/env bash
set -euo pipefail
gaphor_exe="${GAPHOR_EXE:-gaphor}"
unit_only=0
headless=0
while (($#)); do
  case "$1" in
    --gaphor) gaphor_exe="$2"; shift 2 ;;
    --unit-only) unit_only=1; shift ;;
    --headless) headless=1; shift ;;
    *) echo "Opción desconocida: $1" >&2; exit 2 ;;
  esac
done
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export GAPHOR_BPMN_TEST_OUTPUT="$(mktemp -d -t gaphor-bpmn-tests-XXXXXXXX)"
export PYTHONDONTWRITEBYTECODE=1
scripts=(run_in_gaphor.py)
if (( ! unit_only )); then scripts+=(integration.py); fi
for script in "${scripts[@]}"; do
  if ((headless)); then
    xvfb-run -a "$gaphor_exe" exec "$script_dir/tests/$script"
  else
    "$gaphor_exe" exec "$script_dir/tests/$script"
  fi
  prefix=""
  report="results.txt"
  if [[ "$script" == integration.py ]]; then prefix="integration-"; report="integration.txt"; fi
  cat "$GAPHOR_BPMN_TEST_OUTPUT/$report"
  [[ "$(cat "$GAPHOR_BPMN_TEST_OUTPUT/${prefix}status.txt")" == PASS ]]
done
echo "Modelos temporales, capturas y resultados: $GAPHOR_BPMN_TEST_OUTPUT"
