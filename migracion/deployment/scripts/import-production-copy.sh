#!/usr/bin/env bash
# One-time full historical Render production clone into an EMPTY private target.
# Does not start the backend, clean/repair Flyway, or enable public access.
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/common.sh"
EXTRA_COMPOSE_FILES=("$DEPLOYMENT_DIR/compose.pilot.yaml")
[[ $# -eq 2 ]] || die 'Uso: sudo bash scripts/import-production-copy.sh <staging.env|production.env> </srv/exotic/private/import-dir>'
[[ "$EUID" -eq 0 ]] || die 'La restauracion requiere sudo para escribir el volumen Docker aislado.'
load_environment "$1"
validate_runtime_inputs private-pilot
require_prepared
acquire_operation_lock
snapshot=$(realpath -e -- "$2")
[[ "$snapshot" == /srv/exotic/private/* && -d "$snapshot" ]] || die 'El respaldo debe estar dentro de /srv/exotic/private/.'
for name in production.dump production.documents.tar.gz documents.before.sha256z documents.after.sha256z SHA256SUMS; do
    validate_private_file "$snapshot/$name" "$name"
done
private_dir=$(dirname -- "$ENV_FILE")
[[ ! -e "$private_dir/bootstrap.complete.json" && ! -e "$private_dir/import.restored.json" ]] || die 'El entorno ya tiene un registro de importacion; no se sobrescribe.'
backend_id=$(dc ps --all --quiet backend)
if [[ -n "$backend_id" ]]; then
    [[ "$(docker inspect --format '{{.State.Running}}' "$backend_id")" == false ]] || die 'El backend debe estar detenido antes de restaurar.'
fi
sql() { dc exec -T database psql -XAt --set=ON_ERROR_STOP=1 --username postgres --dbname "$DB_NAME" -c "$1"; }
[[ "$(sql "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_toast%' AND c.relkind IN ('r','p','S','v','m','f');")" == 0 ]] || die 'La base destino contiene objetos; no se borra ni se restaura encima.'
[[ "$(sql 'SELECT count(*) FROM pg_largeobject_metadata;')" == 0 ]] || die 'El destino contiene large objects; no se sobrescribe.'
[[ "$(sql "SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND NOT EXISTS(SELECT 1 FROM pg_depend d WHERE d.classid='pg_proc'::regclass AND d.objid=p.oid AND d.deptype='e');")" == 0 ]] || die 'El destino contiene funciones de usuario; no es una base vacia.'
[[ "$(sql "SELECT count(*) FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND t.typtype IN ('e','d','r') AND NOT EXISTS(SELECT 1 FROM pg_depend d WHERE d.classid='pg_type'::regclass AND d.objid=t.oid AND d.deptype='e');")" == 0 ]] || die 'El destino contiene tipos de usuario; no es una base vacia.'
[[ "$(sql "SELECT (NOT rolsuper AND NOT rolcreatedb AND NOT rolcreaterole AND NOT rolreplication)::text FROM pg_roles WHERE rolname='$DB_USER';")" == true ]] || die 'El rol de aplicacion no cumple los privilegios esperados.'
[[ "$(sql "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname=current_database();")" == "$DB_USER" ]] || die 'El rol de aplicacion debe ser propietario de la base destino.'
uploads_path=$(docker volume inspect --format '{{.Mountpoint}}' "$UPLOADS_VOLUME")
[[ -d "$uploads_path" && -z "$(find "$uploads_path" -mindepth 1 -print -quit)" ]] || die 'El volumen de documentos debe estar vacio.'
umask 077
python3 - "$snapshot" <<'PY'
from pathlib import Path
import hashlib,sys,tarfile
root=Path(sys.argv[1])
lines=(root/'SHA256SUMS').read_text().splitlines()
expected={'production.dump','production.documents.tar.gz'}
assert len(lines)==2
for line in lines:
    digest,name=line.split('  ',1)
    assert name in expected and hashlib.file_digest((root/name).open('rb'),'sha256').hexdigest()==digest
    expected.remove(name)
assert not expected
assert (root/'documents.before.sha256z').read_bytes()==(root/'documents.after.sha256z').read_bytes()
with tarfile.open(root/'production.documents.tar.gz','r:gz') as tf:
    assert all(not m.name.startswith('/') and '..' not in Path(m.name).parts and (m.isfile() or m.isdir()) for m in tf.getmembers())
PY
note "Restaurando respaldo completo en $PROJECT_NAME (backend detenido, destino vacio)."
if ! dc exec -T database pg_restore --username postgres --dbname "$DB_NAME" --role "$DB_USER" \
    --no-owner --no-acl --exit-on-error --single-transaction \
    < "$snapshot/production.dump" > "$private_dir/import.restore.log" 2>&1; then
    die "Fallo transaccional de pg_restore; revisar de forma privada $private_dir/import.restore.log."
fi
python3 - "$snapshot" "$uploads_path" "$private_dir" "$ENVIRONMENT" "$DB_NAME" <<'PY'
from pathlib import Path
import hashlib,json,os,sys,tarfile,datetime
source,target,private=map(Path,sys.argv[1:4])
with tarfile.open(source/'production.documents.tar.gz','r:gz') as tf:
    tf.extractall(target,filter='data')
for p in [target,*target.rglob('*')]:
    os.chown(p,1000,1000)
    p.chmod(0o755 if p.is_dir() else 0o644)
entries=(source/'documents.after.sha256z').read_bytes().split(b'\0')
count=0
for entry in entries:
    if not entry: continue
    digest,name=entry[:64].decode('ascii'),os.fsdecode(entry[66:])
    p=target/name
    assert p.is_file() and hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==digest
    count+=1
assert sum(p.is_file() for p in target.rglob('*'))==count
record={'environment':sys.argv[4],'database':sys.argv[5],'source':'render-production',
        'source_dump_sha256':hashlib.file_digest((source/'production.dump').open('rb'),'sha256').hexdigest(),
        'source_documents_sha256':hashlib.file_digest((source/'production.documents.tar.gz').open('rb'),'sha256').hexdigest(),
        'restored_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'document_files':count,
        'schema_validated':False,'uploads_reviewed':True}
p=private/'import.restored.json'
with p.open('x') as f: json.dump(record,f,indent=2);f.write('\n')
p.chmod(0o600)
print(f'Restored {count} documents; schema comparison and bootstrap approval remain required.')
PY
sql "SELECT count(*) AS tables FROM pg_tables WHERE schemaname='public'; SELECT count(*),count(*) FILTER(WHERE NOT success),max(version::integer) FROM public.flyway_schema_history;"
note 'Restauracion terminada; el backend sigue detenido.'
