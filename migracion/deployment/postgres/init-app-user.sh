#!/usr/bin/env bash
# Executed by the official PostgreSQL entrypoint ONLY on an empty data directory.
# Create the application/database owner separately from the bootstrap superuser.
set -euo pipefail

: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${APP_DB_USER:?APP_DB_USER is required}"
: "${APP_DB_PASSWORD_FILE:?APP_DB_PASSWORD_FILE is required}"
[[ "$APP_DB_USER" != postgres ]] || { printf 'The application role must not be postgres.\n' >&2; exit 1; }
[[ "$APP_DB_USER" =~ ^[a-z][a-z0-9_]{0,62}$ ]] || { printf 'Invalid application role name.\n' >&2; exit 1; }
[[ "$POSTGRES_DB" =~ ^[a-z][a-z0-9_]{0,62}$ ]] || { printf 'Invalid database name.\n' >&2; exit 1; }
[[ -s "$APP_DB_PASSWORD_FILE" ]] || { printf 'Application password file is missing or empty.\n' >&2; exit 1; }

# psql variables are quoted as SQL identifiers/literals, not concatenated SQL.
# Do not enable shell tracing or print this variable.
app_password=$(cat -- "$APP_DB_PASSWORD_FILE")
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --set=ON_ERROR_STOP=1 \
  --set=app_user="$APP_DB_USER" --set=app_password="$app_password" --set=app_database="$POSTGRES_DB" <<'SQL'
CREATE ROLE :"app_user" LOGIN PASSWORD :'app_password'
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
ALTER DATABASE :"app_database" OWNER TO :"app_user";
REVOKE ALL ON DATABASE :"app_database" FROM PUBLIC;
GRANT CONNECT, TEMPORARY ON DATABASE :"app_database" TO :"app_user";
ALTER SCHEMA public OWNER TO :"app_user";
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA public TO :"app_user";
SQL
unset app_password
