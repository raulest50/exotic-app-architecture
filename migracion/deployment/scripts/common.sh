#!/usr/bin/env bash
# Shared library for the Linux deployment scripts; do not execute directly.
# Compose reads the explicit env file. No env file is sourced or evaluated and
# secret-file contents are never read by this library. Requires Bash, Python 3,
# Docker Compose v2 and GNU coreutils on the Linux machine running Docker.

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    printf 'Biblioteca interna; utiliza stack.sh, prepare.sh o backup.sh.\n' >&2
    exit 2
fi

DEPLOYMENT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
COMPOSE_FILE="$DEPLOYMENT_DIR/compose.yaml"
ENV_FILE=''
PROJECT_NAME=''
COMPOSE_JSON=''
EXTRA_COMPOSE_FILES=()

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
note() { printf '%s\n' "$*" >&2; }
require_command() { command -v "$1" >/dev/null 2>&1 || die "Falta el comando: $1"; }

dc() {
    local -a command=(docker compose --project-directory "$DEPLOYMENT_DIR"
        --env-file "$ENV_FILE" -f "$COMPOSE_FILE")
    local extra_file
    for extra_file in "${EXTRA_COMPOSE_FILES[@]}"; do
        command+=(-f "$extra_file")
    done
    if [[ -n "$PROJECT_NAME" ]]; then
        command+=(--project-name "$PROJECT_NAME")
    fi
    "${command[@]}" "$@"
}

# Only scalar, non-secret metadata is returned. Never print COMPOSE_JSON.
json_get() {
    printf '%s' "$COMPOSE_JSON" | python3 -c '
import json, sys
value = json.load(sys.stdin)
try:
    for key in sys.argv[1:]:
        value = value[key]
except (KeyError, TypeError):
    raise SystemExit("Falta un campo requerido en la configuracion Compose.")
if not isinstance(value, (str, int, float, bool)):
    raise SystemExit("El campo Compose debe ser escalar.")
print(str(value).lower() if isinstance(value, bool) else value)
' "$@"
}

metadata() { json_get x-deployment "$1"; }

load_environment() {
    [[ $# -eq 1 ]] || die 'Indica un archivo production.env o staging.env.'
    [[ "$(uname -s)" == Linux ]] || die 'Estos scripts requieren Linux.'
    require_command docker
    require_command python3
    require_command realpath
    require_command stat
    [[ -f "$COMPOSE_FILE" ]] || die 'Falta compose.yaml junto al directorio scripts.'
    [[ -f "$1" && -r "$1" ]] || die 'El archivo de entorno no existe o no es legible.'
    local expected variable value
    case "$(basename -- "$1")" in
        production.env) expected=production ;;
        staging.env) expected=staging ;;
        *) die 'El archivo debe llamarse exactamente production.env o staging.env.' ;;
    esac
    ENV_FILE=$(realpath -e -- "$1")
    dc config --quiet
    COMPOSE_JSON=$(dc config --format json)
    ENVIRONMENT=$(metadata ENVIRONMENT)
    [[ "$ENVIRONMENT" == production || "$ENVIRONMENT" == staging ]] || die 'ENVIRONMENT debe ser production o staging.'
    [[ "$ENVIRONMENT" == "$expected" ]] || die 'ENVIRONMENT no coincide con el nombre del archivo indicado.'
    PROJECT_NAME="exotic-$ENVIRONMENT"
    [[ "$(json_get name)" == "$PROJECT_NAME" ]] || die 'El nombre del proyecto Compose no coincide con el entorno.'
    for variable in DB_NAME DB_USER BACKEND_IMAGE FRONTEND_DIST_DIR \
        POSTGRES_ADMIN_PASSWORD_FILE DB_PASSWORD_FILE JWT_SECRET_FILE \
        BACKEND_PROPERTIES_FILE PUBLIC_DOMAIN API_PUBLIC_DOMAIN \
        APP_COMPATIBILITY_CONFIRMED CADDY_IMAGE BACKUP_REMOTE_URI; do
        value=$(metadata "$variable")
        printf -v "$variable" '%s' "$value"
    done
    [[ "$(json_get services backend environment APP_RUNTIME_ENVIRONMENT)" == "$ENVIRONMENT" ]] || die 'APP_RUNTIME_ENVIRONMENT del backend debe coincidir con ENVIRONMENT.'
    POSTGRES_VOLUME="$PROJECT_NAME-postgres"
    UPLOADS_VOLUME="$PROJECT_NAME-uploads"
    LOGS_VOLUME="$PROJECT_NAME-logs"
    EDGE_NETWORK="$PROJECT_NAME-edge"
}

require_absolute_path() {
    [[ "$1" == /* && "$1" != *$'\n'* && "$1" != *$'\r'* ]] || die "$2 debe ser una ruta Linux absoluta sin saltos de linea."
}

validate_private_file() {
    local path=$1 label=$2 mode
    require_absolute_path "$path" "$label"
    [[ -f "$path" && -r "$path" && -s "$path" ]] || die "$label debe ser un archivo legible y no vacio."
    mode=$(stat -Lc '%a' -- "$path")
    [[ "$mode" == 600 || "$mode" == 400 ]] || die "$label requiere permisos 0600 o 0400."
}

validate_image() {
    python3 -c '
import re, sys
value = sys.argv[1]
tail = value.rsplit("/", 1)[-1]
valid = bool(re.search(r"@sha256:[0-9a-f]{64}$", value))
if not valid and ":" in tail:
    tag = tail.rsplit(":", 1)[1]
    valid = bool(re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}", tag)) and tag.lower() != "latest"
if not valid or any(x in value.lower() for x in ("reemplazar", "placeholder", "changeme")):
    raise SystemExit("La imagen debe tener una etiqueta explicita distinta de latest o un digest SHA256.")
' "$1" || die "Imagen no valida: $2"
}

validate_domain() {
    python3 -c '
import re, sys
host = sys.argv[1].lower()
parts = host.split(".")
valid = len(host) <= 253 and len(parts) >= 2 and all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", p) for p in parts)
reserved = parts[-1] in ("example", "invalid", "test", "localhost") or any(host == d or host.endswith("." + d) for d in ("example.com", "example.org", "example.net"))
if not valid or reserved or "reemplazar" in host or "changeme" in host:
    raise SystemExit("Dominio pendiente o no valido: utiliza un nombre DNS real, sin esquema, ruta ni puerto.")
' "$1" || die "Revisa $2."
}

# Syntax/placeholder check only; does not establish bucket access or existence.
valid_remote_uri() {
    python3 -c '
import ipaddress, re, sys
from urllib.parse import urlsplit
value = sys.argv[1]
try:
    u = urlsplit(value)
except ValueError:
    raise SystemExit(1)
bucket = u.netloc
valid = u.scheme == "gs" and bool(re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,220}[a-z0-9]", bucket)) and bool(u.path.strip("/"))
valid = valid and not u.query and not u.fragment and not any(c.isspace() or ord(c) < 32 or c in "*?[]\\" for c in value)
valid = valid and not any(p in (".", "..") for p in u.path.split("/"))
valid = valid and not any(word in value.lower() for word in ("reemplazar", "placeholder", "changeme", "example"))
try:
    ipaddress.ip_address(bucket)
    valid = False
except ValueError:
    pass
raise SystemExit(0 if valid else 1)
' "$1"
}

validate_runtime_inputs() {
    local access_mode=${1:-public}
    case "$access_mode" in
        public)
            [[ "$APP_COMPATIBILITY_CONFIRMED" == true ]] || die 'APP_COMPATIBILITY_CONFIRMED debe ser true tras revisar compatibilidad de la aplicacion.'
            validate_domain "$PUBLIC_DOMAIN" PUBLIC_DOMAIN
            validate_domain "$API_PUBLIC_DOMAIN" API_PUBLIC_DOMAIN
            [[ "$PUBLIC_DOMAIN" != "$API_PUBLIC_DOMAIN" ]] || die 'PUBLIC_DOMAIN y API_PUBLIC_DOMAIN deben ser diferentes.'
            ;;
        private-pilot)
            [[ "$APP_COMPATIBILITY_CONFIRMED" == false ]] || die 'El piloto no confirma compatibilidad para publicacion por dominio.'
            [[ "$PUBLIC_DOMAIN" == localhost && "$API_PUBLIC_DOMAIN" == localhost ]] || die 'El piloto requiere localhost para web y API mediante tunel SSH.'
            ;;
        *) die 'Modo de acceso no reconocido.' ;;
    esac
    [[ "$DB_NAME" =~ ^[a-z][a-z0-9_]{0,62}$ ]] || die 'DB_NAME debe ser un identificador PostgreSQL simple.'
    [[ "$DB_USER" =~ ^[a-z][a-z0-9_]{0,62}$ && "$DB_USER" != postgres ]] || die 'DB_USER debe ser un rol de aplicacion simple distinto de postgres.'
    validate_image "$BACKEND_IMAGE" BACKEND_IMAGE
    validate_image "$CADDY_IMAGE" CADDY_IMAGE
    [[ "$(json_get services backend image)" == "$BACKEND_IMAGE" ]] || die 'La imagen del backend no coincide con x-deployment.'
    require_absolute_path "$FRONTEND_DIST_DIR" FRONTEND_DIST_DIR
    [[ -d "$FRONTEND_DIST_DIR" && -r "$FRONTEND_DIST_DIR/index.html" && -s "$FRONTEND_DIST_DIR/index.html" ]] || die 'FRONTEND_DIST_DIR debe contener un index.html legible y no vacio.'
    validate_private_file "$POSTGRES_ADMIN_PASSWORD_FILE" POSTGRES_ADMIN_PASSWORD_FILE
    validate_private_file "$DB_PASSWORD_FILE" DB_PASSWORD_FILE
    validate_private_file "$JWT_SECRET_FILE" JWT_SECRET_FILE
    validate_private_file "$BACKEND_PROPERTIES_FILE" BACKEND_PROPERTIES_FILE
    local backend_secret
    for backend_secret in "$DB_PASSWORD_FILE" "$JWT_SECRET_FILE" "$BACKEND_PROPERTIES_FILE"; do
        [[ "$(stat -Lc '%u' -- "$backend_secret")" == 1000 ]] || die 'Los secretos montados en backend deben pertenecer al UID 1000; no ampliar sus permisos.'
    done
    [[ "$(realpath -e -- "$POSTGRES_ADMIN_PASSWORD_FILE")" != "$(realpath -e -- "$DB_PASSWORD_FILE")" ]] || die 'Las claves de administrador PostgreSQL y aplicacion deben usar archivos distintos.'
    if [[ "$access_mode" == public && "$ENVIRONMENT" == production ]] && ! valid_remote_uri "$BACKUP_REMOTE_URI"; then
        die 'Produccion requiere BACKUP_REMOTE_URI=gs://bucket-real/prefijo sin placeholders.'
    fi
}

require_docker_engine() {
    [[ "$(docker info --format '{{.OSType}}')" == linux ]] || die 'Se necesita acceso a un Docker Engine Linux.'
}

require_volume() {
    docker volume inspect "$1" >/dev/null 2>&1 || die "Falta el volumen externo $1; utiliza prepare.sh explicitamente."
}

require_prepared() {
    require_docker_engine
    local volume
    for volume in "$POSTGRES_VOLUME" "$UPLOADS_VOLUME" "$LOGS_VOLUME"; do
        require_volume "$volume"
    done
    docker network inspect "$EDGE_NETWORK" >/dev/null 2>&1 || die "Falta la red externa $EDGE_NETWORK; utiliza prepare.sh explicitamente."
    require_writable_application_volumes
}

require_writable_application_volumes() {
    docker run --rm --pull=never --network none --read-only --user 1000:1000 \
        --cap-drop ALL --security-opt no-new-privileges:true \
        --mount "type=volume,src=$UPLOADS_VOLUME,dst=/uploads,volume-nocopy" \
        --mount "type=volume,src=$LOGS_VOLUME,dst=/logs,volume-nocopy" \
        --entrypoint /bin/sh "$CADDY_IMAGE" -ec 'test -w /uploads && test -w /logs' \
        || die 'UID 1000 no puede escribir documentos/logs, o falta la imagen Caddy local. Revisar los volumenes existentes sin cambiar propietarios recursivamente.'
}

# Operators must use the same Linux account. Manual Docker/SQL operations must
# also respect this maintenance window; an advisory lock cannot prevent them.
acquire_operation_lock() {
    require_command flock
    local lock_file="/run/lock/$PROJECT_NAME.lock"
    (umask 077; : >> "$lock_file") || die 'No se puede abrir el bloqueo operativo; utiliza la cuenta operadora habitual.'
    exec 9>> "$lock_file"
    flock --nonblock 9 || die "Ya hay otra operacion de despliegue o respaldo para $PROJECT_NAME."
}
