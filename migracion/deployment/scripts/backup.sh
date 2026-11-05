#!/usr/bin/env bash
# Usage: bash scripts/backup.sh <env-file> <absolute-local-backup-directory> --quiesce
# Explicit operation: temporarily stops only this environment's backend if it
# was running; restores it on exit (including errors/INT/TERM). Database must
# already be running and the pinned Caddy image must already exist locally.
# Creates a pg_dump custom archive and a read-only uploads-volume archive.
# Never copies raw PostgreSQL files, secrets, backend.properties or logs.
# Production requires an external gs://bucket/prefix destination and gcloud.
# Staging may retain a local-only backup. No retention or deletion is performed.
# Other writers must also be quiesced by the operator for cross-store consistency.
# A COMPLETE marker is published only after payload copying succeeds. Partial
# local/remote objects are retained for diagnosis; hashes are not a restore test.
set -Eeuo pipefail
umask 077
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/common.sh"

usage() {
    printf 'Uso: bash scripts/backup.sh <production.env|staging.env> <directorio-local-absoluto> --quiesce\n'
    printf 'Detiene temporalmente el backend para respaldar PostgreSQL y uploads; restaura su estado de arranque previo.\n'
}
if [[ $# -eq 1 && ( "$1" == --help || "$1" == -h ) ]]; then usage; exit 0; fi
[[ $# -eq 3 && "$3" == --quiesce ]] || { usage >&2; exit 2; }
load_environment "$1"
acquire_operation_lock
require_command sha256sum
require_command mktemp
require_docker_engine
require_volume "$POSTGRES_VOLUME"
require_volume "$UPLOADS_VOLUME"
validate_image "$CADDY_IMAGE" CADDY_IMAGE
docker image inspect "$CADDY_IMAGE" >/dev/null 2>&1 || die 'La imagen Caddy debe estar disponible localmente antes del respaldo.'

require_absolute_path "$2" 'El directorio de respaldo'
[[ "$2" != *','* ]] || die 'La ruta de respaldo no puede contener comas (sintaxis de mount de Docker).'
BACKUP_ROOT=$(realpath -m -- "$2")
[[ "$BACKUP_ROOT" != / ]] || die 'Utiliza un directorio de respaldos dedicado, no la raiz del sistema.'

reject_nested_destination() {
    local protected
    protected=$(realpath -m -- "$1")
    [[ "$BACKUP_ROOT" != "$protected" && "$BACKUP_ROOT" != "$protected/"* ]] || die 'El destino de respaldo no puede quedar dentro de volumenes o artefactos de la aplicacion.'
}
reject_nested_destination "$DEPLOYMENT_DIR"
if [[ "$FRONTEND_DIST_DIR" == /* ]]; then reject_nested_destination "$FRONTEND_DIST_DIR"; fi
docker_root=$(docker info --format '{{.DockerRootDir}}')
if [[ "$docker_root" == /* ]]; then reject_nested_destination "$docker_root"; fi
for volume in "$POSTGRES_VOLUME" "$UPLOADS_VOLUME" "$LOGS_VOLUME"; do
    if docker volume inspect "$volume" >/dev/null 2>&1; then
        mountpoint=$(docker volume inspect --format '{{.Mountpoint}}' "$volume")
        if [[ -n "$mountpoint" ]]; then reject_nested_destination "$mountpoint"; fi
    fi
done

REMOTE_ENABLED=false
if valid_remote_uri "$BACKUP_REMOTE_URI"; then
    require_command gcloud
    REMOTE_ENABLED=true
elif [[ "$ENVIRONMENT" == production ]]; then
    die 'Produccion requiere BACKUP_REMOTE_URI=gs://bucket-real/prefijo y acceso de gcloud.'
else
    note 'Staging: respaldo solamente local; no hay un BACKUP_REMOTE_URI valido.'
fi

DATABASE_ID=$(dc ps --quiet --status running database)
[[ -n "$DATABASE_ID" && "$DATABASE_ID" != *$'\n'* ]] || die 'Se necesita exactamente un contenedor database en ejecucion.'
actual_db=$(dc exec -T database sh -ec 'printf "%s\n%s\n" "$POSTGRES_USER" "$POSTGRES_DB"')
[[ "$actual_db" == $'postgres\n'"$DB_NAME" ]] || die 'La identidad PostgreSQL del contenedor no coincide con este archivo de entorno.'
BACKEND_ID=$(dc ps --quiet --status running backend)
[[ "$BACKEND_ID" != *$'\n'* ]] || die 'El respaldo admite una unica instancia de backend.'
DATABASE_IMAGE_ID=$(docker inspect --format '{{.Image}}' "$DATABASE_ID")
BACKEND_IMAGE_ID=''
if [[ -n "$BACKEND_ID" ]]; then BACKEND_IMAGE_ID=$(docker inspect --format '{{.Image}}' "$BACKEND_ID"); fi

mkdir -p -- "$BACKUP_ROOT"
STARTED_AT=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
WORK_DIR=$(mktemp -d "$BACKUP_ROOT/.partial-$PROJECT_NAME-$(date -u '+%Y%m%dT%H%M%SZ')-XXXXXX")
RUN_ID=${WORK_DIR##*/}
RUN_ID=${RUN_ID#.partial-}
PAYLOAD_DIR="$WORK_DIR/$RUN_ID"
mkdir -- "$PAYLOAD_DIR"
RESTORE_BACKEND=false

resume_backend() {
    if [[ "$RESTORE_BACKEND" == true ]]; then
        if ! dc start --wait --wait-timeout 180 backend; then
            return 1
        fi
        RESTORE_BACKEND=false
    fi
}

finish() {
    local result=$?
    trap - EXIT INT TERM
    if [[ "$RESTORE_BACKEND" == true ]]; then
        if resume_backend; then
            note "Backend de $PROJECT_NAME restaurado tras finalizar el respaldo."
        else
            note "ERROR: no se pudo recuperar el backend de $PROJECT_NAME; requiere intervencion."
            result=1
        fi
    fi
    if [[ "$result" -ne 0 ]]; then
        note "Respaldo incompleto; se conserva el directorio parcial: $WORK_DIR"
        note 'No considerar completos objetos remotos que no tengan marcador COMPLETE.'
    fi
    exit "$result"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

if [[ -n "$BACKEND_ID" ]]; then
    RESTORE_BACKEND=true
    dc stop --timeout 60 backend
fi

dc exec -T database sh -ec 'exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner --no-acl' > "$PAYLOAD_DIR/database.dump"
[[ -s "$PAYLOAD_DIR/database.dump" ]] || die 'El archivo pg_dump esta vacio.'
dc exec -T database pg_restore --list < "$PAYLOAD_DIR/database.dump" >/dev/null
docker run --rm --pull=never --network none --read-only \
    --security-opt no-new-privileges \
    --mount "type=volume,src=$UPLOADS_VOLUME,dst=/source,readonly" \
    --mount "type=bind,src=$PAYLOAD_DIR,dst=/backup" \
    --entrypoint tar "$CADDY_IMAGE" -czf /backup/uploads.tar.gz -C /source .
ARCHIVED_AT=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

# Resume normal application operation before potentially slow cloud copying.
resume_backend
python3 - "$PAYLOAD_DIR/manifest.json" "$ENVIRONMENT" "$DB_NAME" "$DB_USER" \
    "$BACKEND_IMAGE" "$DATABASE_IMAGE_ID" "$BACKEND_IMAGE_ID" "$STARTED_AT" "$ARCHIVED_AT" <<'PY'
import json, sys
path, environment, database, user, image, db_id, backend_id, started, archived = sys.argv[1:]
manifest = {
    "format_version": 1, "environment": environment,
    "database": database, "application_database_role": user,
    "backend_image_reference": image, "database_image_id": db_id,
    "running_backend_image_id": backend_id or None,
    "started_at_utc": started, "archives_created_at_utc": archived,
    "payload": ["database.dump", "uploads.tar.gz"],
    "database_format": "pg_dump custom, no owner/ACL",
    "consistency": "backend stopped if previously running; operator excludes other writers",
    "completion": "require a separate COMPLETE marker; manifest alone does not prove completion",
}
with open(path, "x", encoding="utf-8") as stream:
    json.dump(manifest, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
PY
(
    cd -- "$PAYLOAD_DIR"
    sha256sum database.dump uploads.tar.gz manifest.json > SHA256SUMS
    sha256sum --check --status SHA256SUMS
)

if [[ "$REMOTE_ENABLED" == true ]]; then
    gcloud storage cp --recursive "$PAYLOAD_DIR" "${BACKUP_REMOTE_URI%/}/"
fi
printf 'Payload verificado; copia finalizada: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$WORK_DIR/COMPLETE"
if [[ "$REMOTE_ENABLED" == true ]]; then
    gcloud storage cp "$WORK_DIR/COMPLETE" "${BACKUP_REMOTE_URI%/}/$RUN_ID/COMPLETE"
fi
mv -- "$WORK_DIR/COMPLETE" "$PAYLOAD_DIR/COMPLETE"
FINAL_DIR="$BACKUP_ROOT/$RUN_ID"
[[ ! -e "$FINAL_DIR" ]] || die 'El destino final del respaldo ya existe.'
mv -- "$PAYLOAD_DIR" "$FINAL_DIR"
note "Respaldo completo: $FINAL_DIR"
if [[ "$REMOTE_ENABLED" == true ]]; then note "Copia externa completa: ${BACKUP_REMOTE_URI%/}/$RUN_ID/"; fi
# Keep the empty .partial directory as an operational trace; no automatic deletion.
