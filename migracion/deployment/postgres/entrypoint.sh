#!/usr/bin/env bash
# Compose file-backed secrets preserve host ownership. The init script runs as
# postgres, so prepare its app-password copy in private tmpfs while still root.
# No password is printed, embedded in the image or exported as a custom env var.
set -euo pipefail
[[ "$(id -u)" == 0 ]] || { printf 'The database bootstrap wrapper requires container root.\n' >&2; exit 1; }
[[ -s /run/secrets/DB_PASSWORD ]] || { printf 'Missing application database secret.\n' >&2; exit 1; }
install -d -m 0700 -o postgres -g postgres /run/exotic-bootstrap
install -m 0400 -o postgres -g postgres /run/secrets/DB_PASSWORD /run/exotic-bootstrap/app-password
exec /usr/local/bin/docker-entrypoint.sh "$@"
