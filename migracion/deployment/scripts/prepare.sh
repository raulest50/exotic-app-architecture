#!/usr/bin/env bash
# Usage: bash scripts/prepare.sh <production.env|staging.env>
# Explicit, idempotent preparation: creates three named external volumes and
# one edge network if absent. Does not install Docker, create secrets, copy
# application files, start services, delete data or change existing resources.
# New uploads/log volumes get UID 1000 ownership; existing volumes are checked.
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/common.sh"

usage() { printf 'Uso: bash scripts/prepare.sh <production.env|staging.env>\nCrea volumenes y red externos del entorno; no instala ni despliega.\n'; }
if [[ $# -eq 1 && ( "$1" == --help || "$1" == -h ) ]]; then usage; exit 0; fi
[[ $# -eq 1 ]] || { usage >&2; exit 2; }
load_environment "$1"
acquire_operation_lock
require_docker_engine

for volume in "$POSTGRES_VOLUME" "$UPLOADS_VOLUME" "$LOGS_VOLUME"; do
    if docker volume inspect "$volume" >/dev/null 2>&1; then
        note "Volumen existente conservado: $volume"
    else
        docker volume create --label "exotic.environment=$ENVIRONMENT" "$volume" >/dev/null
        if [[ "$volume" == "$UPLOADS_VOLUME" || "$volume" == "$LOGS_VOLUME" ]]; then
            docker run --rm --pull=never --network none --read-only \
                --cap-drop ALL --cap-add CHOWN \
                --mount "type=volume,src=$volume,dst=/target,volume-nocopy" \
                --entrypoint /bin/sh "$CADDY_IMAGE" -ec 'chmod 0755 /target; chown 1000:1000 /target'
        fi
        note "Volumen creado: $volume"
    fi
done

if docker network inspect "$EDGE_NETWORK" >/dev/null 2>&1; then
    note "Red existente conservada: $EDGE_NETWORK"
else
    docker network create --driver bridge --label "exotic.environment=$ENVIRONMENT" "$EDGE_NETWORK" >/dev/null
    note "Red creada: $EDGE_NETWORK"
fi

require_writable_application_volumes
