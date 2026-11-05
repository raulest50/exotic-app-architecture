#!/usr/bin/env bash
# Usage: bash scripts/stack.sh <validate|up|status|stop|down> <env-file>
# validate reads configuration/files locally; it does not contact the Docker
# daemon. Other actions operate on the explicit environment only. down never
# removes volumes. No installs, image builds or source changes are performed.
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/common.sh"

usage() {
    printf 'Uso: bash scripts/stack.sh <validate|up|status|stop|down> <production.env|staging.env>\n'
    printf 'validate: preflight local; up: valida y arranca; status: consulta; stop: detiene; down: retira contenedores sin borrar volumenes.\n'
}

if [[ $# -eq 1 && ( "$1" == --help || "$1" == -h ) ]]; then usage; exit 0; fi
[[ $# -eq 2 ]] || { usage >&2; exit 2; }
action=$1
case "$action" in validate|up|status|stop|down) ;; *) usage >&2; exit 2 ;; esac
load_environment "$2"
case "$action" in up|stop|down) acquire_operation_lock ;; esac

case "$action" in
    validate)
        validate_runtime_inputs
        note "Preflight local correcto para $PROJECT_NAME; no verifica DNS, permisos cloud, capacidad ni salud del despliegue."
        ;;
    up)
        validate_runtime_inputs
        require_prepared
        dc up -d --wait --wait-timeout 180
        ;;
    status) dc ps --all ;;
    stop) dc stop ;;
    down)
        note "Retirando contenedores de $PROJECT_NAME; los volumenes se conservan."
        dc down
        ;;
esac
