#!/usr/bin/env bash
# Private VM environments; no public domain readiness is asserted by this script.
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/common.sh"
EXTRA_COMPOSE_FILES=("$DEPLOYMENT_DIR/compose.pilot.yaml")

usage() {
    printf 'Uso: bash scripts/pilot.sh <validate|database|web|up|status|stop|down> <staging.env|production.env>\n'
}
[[ $# -eq 2 ]] || { usage >&2; exit 2; }
action=$1
case "$action" in validate|database|web|up|status|stop|down) ;; *) usage >&2; exit 2 ;; esac
load_environment "$2"

# Check the effective model, including the override, before every operation.
printf '%s' "$COMPOSE_JSON" | python3 -c '
import json,sys
services=json.load(sys.stdin)["services"]
for name in ("database","backend","web"):
    if services[name].get("ports"):
        raise SystemExit("Solo el proyecto edge puede publicar puertos loopback; las aplicaciones no publican puertos.")
'

case "$action" in database|web|up|stop|down) acquire_operation_lock ;; esac
case "$action" in
    validate) validate_runtime_inputs private-pilot ;;
    database|web)
        validate_runtime_inputs private-pilot
        require_prepared
        service=$action
        dc up -d --no-deps --wait --wait-timeout 240 "$service"
        ;;
    up)
        validate_runtime_inputs private-pilot
        require_prepared
        bootstrap_record="$(dirname -- "$ENV_FILE")/bootstrap.complete.json"
        validate_private_file "$bootstrap_record" bootstrap.complete.json
        python3 -c '
import json,sys
with open(sys.argv[1],encoding="utf-8") as stream:
    record=json.load(stream)
if record.get("environment")!=sys.argv[3] or record.get("database")!=sys.argv[2] or record.get("source") not in ("render-production","render-staging","demo") or record.get("schema_validated") is not True or record.get("uploads_reviewed") is not True:
    raise SystemExit("Falta una revision registrada de esquema y documentos del entorno.")
if sys.argv[3]=="production" and record.get("source")!="render-production":
    raise SystemExit("La copia privada de produccion requiere el origen Render produccion.")
if record.get("backend_image_id")!=sys.argv[4] or len(record.get("source_dump_sha256",""))!=64:
    raise SystemExit("La aprobacion debe corresponder a esta imagen y a una copia identificada por SHA256.")
' "$bootstrap_record" "$DB_NAME" "$ENVIRONMENT" "$(docker image inspect --format '{{.Id}}' "$BACKEND_IMAGE")"
        note 'Piloto privado: la compatibilidad de los dominios publicos sigue pendiente.'
        dc up -d --wait --wait-timeout 900
        ;;
    status) dc ps --all ;;
    stop) dc stop ;;
    down) dc down ;;
esac
