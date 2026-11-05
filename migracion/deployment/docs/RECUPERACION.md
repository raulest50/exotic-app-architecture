# Respaldo, restauración y reversión

El 4 de noviembre de 2026 se exporto Render produccion en modo lectura y se
restauro la misma copia completa en staging y produccion de la VM: 145 tablas,
115 registros Flyway y 122 documentos por entorno. La comparacion prearranque
incluyo hashes de todas las tablas, secuencias, historial, objetos binarios y
documentos. Registro: [DESPLIEGUE_INICIAL.md](DESPLIEGUE_INICIAL.md).
El corte publico, el respaldo externo periodico y su recuperacion siguen
pendientes; esta restauracion no demuestra recuperacion ante perdida de la VM.

## Importacion inicial ejecutada

`scripts/import-production-copy.sh <entorno.env> <directorio-privado>` requiere
sudo, backend detenido, base y documentos vacios, y una copia verificada bajo
`/srv/exotic/private/`. Restaura esquema, datos, secuencias, objetos binarios e
historial con `--single-transaction --no-owner --no-acl --role` del destino.
No ejecuta `clean`, `repair`, baseline ni consolidacion V1.

Los archivos de origen son `production.dump`, `production.documents.tar.gz`,
`documents.before.sha256z`, `documents.after.sha256z` y `SHA256SUMS`. No usan el
marcador `COMPLETE` del procedimiento futuro de `backup.sh`. Su captura esta
registrada en el directorio privado de importacion.

La restauracion SQL es atomica; la extraccion de documentos posterior es otra
operacion. Si falla esa segunda fase, detenerse y revisar el estado registrado:
la base puede estar restaurada y el script rehusara sobrescribirla. Resolver
la recuperacion explicitamente, sin borrar datos para repetir el comando.

El script deja `import.restored.json`. Solo tras comparar el esquema/historial,
la imagen y los documentos se genera `bootstrap.complete.json`; `pilot.sh up`
contrasta su entorno, base, origen e Image ID. La copia privada de produccion
no equivale a habilitar dominios ni a configurar backups remotos.

## Qué protege cada mecanismo

- Los volúmenes conservan PostgreSQL, documentos y registros al recrear
  contenedores. No sustituyen una copia fuera de la VM.
- `backup.sh` genera un dump lógico PostgreSQL y un archivo de `/app/data`.
  Se pausa este backend para evitar escrituras de la app mientras se capturan
  ambos. El operador debe excluir otros escritores y operaciones manuales.
- Los scripts utilizan un bloqueo por entorno. No operar con otro checkout,
  otra cuenta o comandos Docker/SQL manuales durante ese mantenimiento.
- La copia externa se guarda bajo un identificador único. `COMPLETE` aparece
  después de copiar los archivos; un prefijo sin marcador debe tratarse como
  incompleto, aunque contenga un manifest o archivos con nombres correctos.
- Conservar las imágenes y artefactos de cada versión en el registro/CI, y
  respaldar configuración privada y secretos por un canal seguro separado.
  El script no incluye secretos, registros, certificados ni archivos físicos
  del clúster PostgreSQL. Los certificados conservan sus volúmenes; si se pierde
  el disco, planificar su recuperación segura o reemisión y sus límites ACME.

## Crear un respaldo

Ejemplo futuro, desde el directorio deployment de la VM:

```bash
bash scripts/backup.sh /srv/exotic/private/staging/staging.env /srv/exotic-backups/staging --quiesce
```

El comando es operativo: detiene temporalmente el backend si estaba arrancado.
Al terminar o fallar intenta recuperarlo; un error de recuperación requiere
intervención y se devuelve como fallo. Si ya estaba parado, lo conserva parado.
PostgreSQL debe estar arrancado. La imagen Caddy usada para archivar debe estar
ya descargada; el script no compila ni descarga imágenes durante el respaldo.

El directorio terminado contiene:

```text
database.dump     pg_dump custom; sin owner/ACL del entorno original
uploads.tar.gz    documentos del volumen de la aplicación
manifest.json     entorno, base, rol, imágenes y fechas; sin secretos
SHA256SUMS        integridad de los tres archivos anteriores
COMPLETE          marcador de finalización
```

En producción se exige un `BACKUP_REMOTE_URI=gs://bucket/prefijo` real y acceso
mediante `gcloud storage`. Staging puede ensayar una copia local. Para ambos,
comprobar existencia de los objetos remotos y descarga/restauración; una URI
válida no acredita permisos. Los directorios parciales se conservan ante error.
No hay borrado automático ni política de retención configurada por estos scripts.

## Restaurar en un destino nuevo y vacío

Estas operaciones escriben datos. Usar una VM o Docker Engine aislado del
entorno vigente, con el destino explícitamente acordado. No eliminar volúmenes
actuales para fabricar un destino vacío y no restaurar encima de datos vivos.

1. Recuperar una copia completa desde un origen de confianza, comprobar
   `COMPLETE` y ejecutar `sha256sum --check SHA256SUMS` dentro del directorio.
   Revisar el manifest y las versiones. Los hashes detectan corrupción, no
   autentican por sí solos un origen desconocido.
2. Preparar la configuración privada del destino, sus secretos independientes,
   artefactos de la versión y volúmenes externos nuevos según README. No activar
   el sitio público. Mantener el backend y web parados durante la restauración.
3. Desde deployment, seleccionar explícitamente el archivo privado y arrancar
   solo PostgreSQL:

```bash
ENV_FILE=/srv/exotic/private/staging/staging.env
docker compose --env-file "$ENV_FILE" -f compose.yaml up -d --wait database
```

4. Comprobar que la base de destino no contiene tablas o relaciones de
   aplicación. Consultar el resultado antes de continuar:

```bash
docker compose --env-file "$ENV_FILE" -f compose.yaml exec -T database sh -ec \
  'exec psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -At -v ON_ERROR_STOP=1' <<'SQL'
SELECT count(*)
FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
  AND n.nspname NOT LIKE 'pg_toast%'
  AND c.relkind IN ('r', 'p', 'v', 'm', 'S');
SQL
```

Solo un resultado cero permite seguir con este procedimiento de destino vacío.
Si hay datos, detenerse y determinar otro destino; no añadir `--clean` para
sobrescribir un entorno existente.

5. Restaurar `database.dump` de la copia descargada. El rol de aplicación ya fue
   creado por init. Se asigna el contenido al rol del destino, sin borrar objetos:

```bash
docker compose --env-file "$ENV_FILE" -f compose.yaml exec -T database sh -ec \
  'exec pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --role="$APP_DB_USER" --no-owner --no-acl --exit-on-error --single-transaction' \
  < /ruta/privada/a/la/copia/database.dump
```

6. Restaurar los documentos en el volumen uploads **del destino**, después de
   verificar que está vacío. El ejemplo siguiente es solo para staging; no usar
   el volumen de producción ni dejar que Docker cree silenciosamente un volumen
   por un error de nombre:

```bash
docker volume inspect exotic-staging-uploads >/dev/null
docker run --rm --pull=never --network none --read-only \
  --mount type=volume,src=exotic-staging-uploads,dst=/target \
  --mount type=bind,src=/ruta/privada/a/la/copia,dst=/backup,readonly \
  --entrypoint sh caddy:2-alpine@sha256:e70b164da81ef698b3ad19af799ea6086ce6d9e48ed4079eb9fe26f6fbf14ee5 -ec \
  'test -z "$(ls -A /target)" && tar -xzf /backup/uploads.tar.gz -C /target'
```

7. Conservar el historial Flyway restaurado. Revisar qué migraciones aplicará la
   imagen elegida antes de arrancar Spring. Mantener Flyway habilitado e
   Hibernate `validate`; no editar checksums ni desactivar validación para
   conseguir el arranque.
8. Habilitar la compatibilidad del destino solo cuando esté revisada y arrancar
   mediante `stack.sh up`. Comprobar login, permisos, lectura de documentos,
   carga/descarga y operaciones de negocio representativas. No apuntar estas
   comprobaciones a Render producción para suplir fallos del destino.
9. Registrar duración, pérdida de datos prevista y pasos necesarios de DNS para
   contrastarlos con los objetivos de recuperación antes de producción.

## Corte y reversión

La primera migración desde Render necesita una copia final coordinada de base y
documentos, control de escrituras y validación antes de cambiar usuarios/DNS.
El script local no migra automáticamente Render ni crea por sí solo esa ventana.

Conservar una versión anterior de backend/frontend facilita revertir código
cuando el esquema sigue siendo compatible. Un rollback de imagen no deshace
DDL, datos o migraciones Flyway. Si se requiere restaurar, hacerlo mediante el
procedimiento acordado, con las consecuencias de pérdida de cambios posteriores
al respaldo conocidas. No utilizar dos bases productivas con escrituras
independientes durante la transición.

Referencia: [PostgreSQL 18, dump y restauración](https://www.postgresql.org/docs/18/backup-dump.html).
