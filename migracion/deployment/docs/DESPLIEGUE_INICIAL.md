# Despliegue inicial: produccion y staging privados

Actualizado el **4 de noviembre de 2026**. Se restauraron ambos entornos de la
VM desde **una unica exportacion de Render produccion**. Los dos entornos estan
activos: seis servicios saludables y el proxy compartido operativo. La API,
los recursos web y el acceso privado se verificaron. La auditoria de Render
que sigue conserva el contexto de la decision anterior a la restauracion.

**Revision posterior, 5 de noviembre:** se actualizaron las dos webs y los dos
backends para preparar cuatro subdominios, conservando datos, volumenes y SSH.
La imagen vigente es `exotic-backend:vm-domains-20261105-be80296d2`, del mismo
commit base mas unicamente CORS configurable. Los frontends agregan seleccion
explicita de API/entorno y artefactos separados para acceso publico y SSH.
El edge vigente utiliza `compose.edge.yaml` y `/srv/exotic/private/edge/edge.env`:
TCP80/443 publico mas los cuatro listeners loopback. DNS, certificados ACME y
confirmacion de reserva de IP siguen pendientes. La evidencia actual y el
Image ID estan en [SUBDOMINIOS.md](SUBDOMINIOS.md). Los datos y resultados del
4 de noviembre que siguen se conservan como registro historico.

## Alcance y versiones

- VM Google Compute Engine `vm-produccion`, `34.30.31.30`, Debian 13.7,
  2 vCPU y 9949 MiB de RAM reconocida. Docker Engine 29.9.3 y Compose 5.7.0.
- Backend de ambos entornos: commit
  `80296d2995d4a8053601f089a17d7df0f6ddd9f4`, Java 21; imagen
  `exotic-backend:vm-staging-80296d2`. La etiqueta historica staging identifica
  el artefacto; el entorno real se fija por `APP_RUNTIME_ENVIRONMENT` y perfil.
- Image ID verificado:
  `sha256:2babdd98ba97e7c429e7df97f0ddcad532879745896438ee02750a344065acde`.
- Frontend de ambos entornos: commit
  `9a3d63fda421d0dce59cd48c7b81f940207e3d94`; Bun 1.3.14 y Vite.
- Construccion fuera de la VM desde archivos del commit, sin configuracion
  privada local. Gradle `build -x test -Pprod` y Vite build completados.
  Los cambios locales no confirmados de backend y consolidacion V1 se preservan
  y no forman parte del artefacto desplegado. No se ejecutaron suites de pruebas.
- PostgreSQL destino 18.6 con imagen fijada por digest; origen Render 18.3.
  Locale origen `en_US.UTF8`, destino `en_US.utf8`, ambos libc/UTF8.

## Copia y comprobaciones antes del arranque

Directorio privado de la VM:
`/srv/exotic/private/import-20261104-render-production` (0700; archivos 0600).
La exportacion se produjo remotamente con pg_dump 18.6 del servicio productivo
de Render; los bytes pasaron directamente por SSH a la VM, sin conversion de
texto PowerShell ni archivos de datos en el checkout.
La captura final transcurrio entre **22:30:03 y 22:30:49 UTC**
(17:30:03 a 17:30:49 Colombia).

| Archivo | SHA256 |
| --- | --- |
| `production.dump` | `5e6e91011a635dda8c2ffec97d117c1ebe45f36c9103a398308cf8cfcaf22803` |
| `production.documents.tar.gz` | `7560dd023941afcb184e68869a1f9722eb838eee2130493748d269630f74c353` |

El dump custom contiene esquema, datos, secuencias, objetos binarios e historial
Flyway. Ambos destinos estaban vacios y con el backend detenido. Se restauro
mediante `import-production-copy.sh`, con el rol propio del destino,
`--no-owner --no-acl --exit-on-error --single-transaction`. No se ejecutaron
clean, repair, baseline ni migraciones de consolidacion V1.

Verificacion terminada a las **22:37:57 UTC / 17:37:57 Colombia**, antes de
arrancar Spring en cualquiera de los dos destinos:

- **145 tablas**: mismos conteos y hashes del contenido completo de cada tabla.
- **123 secuencias**: mismos `last_value` e `is_called`, sin consumir valores.
- Historial Flyway completo identico: **115 registros**, **114 SQL exitosas**,
  baseline version 2, ultima version 118, **cero fallidas**.
- Esquema logico equivalente sin propietarios/ACL, y mismas paginas de large
  objects: **1263 objetos binarios y 1434 paginas**. El TOC de pg_dump 18 los
  agrupa en dos entradas; no son solamente dos objetos. Tablas y secuencias
  pertenecen al rol de su propio entorno.
- **122 documentos**, **94 740 540 bytes** de contenido, restaurados en cada
  volumen uploads. Todos sus hashes coinciden con el manifiesto origen.
- Los manifiestos de archivos antes y despues de la captura coinciden. Esto
  detecta cambios de contenido en ese intervalo; no convierte PostgreSQL y el
  filesystem en una unica transaccion ni cubre escrituras posteriores de Render.
- JAR inspeccionado: los **116 archivos de migraciones versionadas** coinciden
  por SHA256 con el commit; los **114 checksums aplicados** coinciden con el
  historial. V1 y V2 historicas permanecen empaquetadas, sin ejecutarse otra vez.
  No contiene configuracion privada, `FlywayConsolidatedConfig`, `migration-v1`
  ni `bootstrap-v1`. SHA256 del JAR:
  `793cbaa594beb73a3b6c1578e1adc6547ce6aa14a16aa724b216bbe1af6f77f9`.

Los resultados agregados estan en `verification-before-start.json` y archivos
privados de hashes. Cada entorno dispone de `import.restored.json` y
`bootstrap.complete.json`, vinculados al mismo dump y al Image ID revisado.
Una vez arrancada la aplicacion, inicializadores y tareas programadas pueden
modificar cada copia de forma independiente; no exigir identidad posterior.

## Resultado del arranque y verificacion final

Comprobado a las **22:54:54 UTC / 17:54:54 Colombia**:

- Staging: Spring arranco en **371,496 s** (proceso 386,101 s), cuota 0,20 vCPU.
  Produccion: **108,101 s** (proceso 112,265 s), cuota 0,65 vCPU. Los
  contenedores finales tienen **cero reinicios**.
- JPA EntityManagerFactory inicializado en ambos destinos con Hibernate
  `validate`, Flyway habilitado e historial completo inalterado despues del
  arranque. Logback del commit fija la salida de Flyway en OFF; la evidencia
  conservada es la configuracion efectiva, checksums, arranque e historial,
  no una linea de log `Successfully validated` que no se emitio.
- HTTP 200 de ambos frontends, sus **14 recursos JS/CSS de entrada** y fallback
  SPA. HTTP 200 de `/api/auth/me` con autenticacion y
  `/productos/unidades-medida`; HTTP 401 sin autenticacion.
- CORS para `http://localhost:5173` correcto; diagnosticos reservados al entorno
  local permanecen bloqueados. Un JWT de staging es rechazado en produccion y
  viceversa. Los JWT de comprobacion tuvieron vida corta, permanecieron en
  memoria y no requirieron leer ni cambiar contrasenas de usuarios.
- **El login con contrasena del usuario queda para comprobacion manual**.
  No se crearon usuarios ni se cambiaron sus credenciales. No se presenta este
  smoke check como validacion de todos los flujos de negocio ni como e2e.
- Mismos hashes de los **122 documentos** despues del arranque. Escritura y
  lectura temporal desde UID 1000 comprobada en documentos/logs de ambos
  backends; los marcadores se retiraron al terminar.
- Bases y esquemas pertenecen a los roles propios, sin superusuario,
  creacion de roles/bases ni replicacion. Extensiones `pg_trgm` 1.6 y `plpgsql`
  1.0; 145 tablas y 115 registros Flyway (0 fallidos) por destino.
- Solo edge publica cuatro bindings IPv4 loopback; las seis aplicaciones no
  publican puertos. Los limites efectivos suman **1,40 vCPU y 6912 MiB**.

Observacion puntual tras estas comprobaciones, sin carga representativa:
backend produccion **477 MiB**, staging **501,3 MiB**; PostgreSQL **83,66 / 68,28
MiB**; web **18,79 / 15 MiB**, edge **12,16 MiB**. Host: **8016 MiB disponibles**,
raiz **4,5 GiB usados / 43 GiB libres**, sin swap. No son garantias bajo carga.
Resultados privados: `verification-after-start.json` y `final-inventory.json`.

## Aislamiento y persistencia

| Entorno | Base y rol | Volumen PostgreSQL | Documentos | Logs |
| --- | --- | --- | --- | --- |
| Staging | `exotic_staging` | `exotic-staging-postgres` | `exotic-staging-uploads` | `exotic-staging-logs` |
| Produccion | `exotic_production` | `exotic-production-postgres` | `exotic-production-uploads` | `exotic-production-logs` |

Las credenciales de administrador, aplicacion y JWT se generaron nuevamente
en la VM y son distintas para cada entorno. No se reutilizaron secretos de
Render ni propiedades privadas locales. Los directorios privados son
`/srv/exotic/private/staging` y `/srv/exotic/private/production`.

El backend usa UID/GID 1000; sus tres secretos montados tienen propietario
1000 y modo 0600. Datos y logs son escribibles por ese usuario. Los montajes
de documentos/logs usan `nocopy` para que Docker no reemplace la propiedad
preparada al inicializar un volumen vacio. La raiz del contenedor es de solo
lectura; tmpfs ofrece el espacio temporal. Flyway sigue habilitado, baseline
automatico desactivado, clean deshabilitado e Hibernate `validate`.

Ambas configuraciones SMTP apuntan a `127.0.0.1:2525`, sin autenticacion ni
credenciales productivas, con timeouts cortos. Se impiden correos duplicados
desde las copias; configuracion real de correo queda para el corte acordado.

Los volumenes externos se conservan al recrear contenedores o usar `down`.
Persistencia no equivale a backup: el disco de la VM es un punto de fallo
compartido. El backup remoto periodico y su recuperacion estan pendientes.
El modo publico sigue bloqueado por compatibilidad y backup remoto sin definir.

## Acceso privado desde Windows

Siete contenedores previstos: tres por entorno y un Caddy compartido.
Las aplicaciones y PostgreSQL no publican puertos del host. Solo edge publica:
El proxy comparte las dos redes: separa las rutas y credenciales, pero no es
una frontera de aislamiento fuerte ante un contenedor comprometido. Ambos
entornos comparten tambien la VM y su disco.

| Binding de la VM | Destino |
| --- | --- |
| `127.0.0.1:15173` | web staging |
| `127.0.0.1:18080` | API staging |
| `127.0.0.1:13000` | web produccion |
| `127.0.0.1:18081` | API produccion |

En PowerShell, desde `C:\Users\hardp\Desktop\exotic_ws\ssh_gcloud`, con Pageant
abierto y la clave cargada, elegir **un entorno a la vez**.

Staging:

```powershell
ssh -F .\pageant-gcloud.conf -o BatchMode=yes -o StrictHostKeyChecking=yes -o UpdateHostKeys=no -o ExitOnForwardFailure=yes -N -L 127.0.0.1:5173:127.0.0.1:15173 -L 127.0.0.1:8080:127.0.0.1:18080 prodexotic@34.30.31.30
```

Produccion:

```powershell
ssh -F .\pageant-gcloud.conf -o BatchMode=yes -o StrictHostKeyChecking=yes -o UpdateHostKeys=no -o ExitOnForwardFailure=yes -N -L 127.0.0.1:5173:127.0.0.1:13000 -L 127.0.0.1:8080:127.0.0.1:18081 prodexotic@34.30.31.30
```

Abrir `http://localhost:5173` y dejar la terminal abierta. Para cambiar de
entorno cerrar primero el tunel con Ctrl+C y abrir el otro. Los puertos locales
5173/8080 deben estar libres; usar otro puerto web no cambia la API elegida
por el frontend existente. La etiqueta visual puede decir local por el hostname;
el backend conserva staging o production segun su configuracion real.
No se deja ningun servidor Vite ni backend local ejecutandose.

## Operacion de la VM

Desde `/srv/exotic/deployment`, mediante `prodexotic`:

```bash
sudo bash scripts/pilot.sh status /srv/exotic/private/staging/staging.env
sudo bash scripts/pilot.sh status /srv/exotic/private/production/production.env
sudo bash scripts/pilot.sh up /srv/exotic/private/staging/staging.env
sudo bash scripts/pilot.sh up /srv/exotic/private/production/production.env
sudo docker compose --project-directory /srv/exotic/deployment --env-file /srv/exotic/private/edge/edge.env -f compose.edge.yaml ps
```

`compose.edge.private.yaml` fue el edge inicial y es una alternativa independiente;
no combinar ambos archivos en un comando Compose. Un cambio solo del `dist`
frontend no requiere reiniciar PostgreSQL ni backend; actualizar la ruta y
recrear exclusivamente `web` con Compose y ambos archivos de aplicacion.
Cambiar imagen backend exige revisar la compatibilidad y actualizar la
aprobacion vinculada a su Image ID.

## Recursos y limites de la entrega

| Contenedor | CPU maxima | RAM maxima |
| --- | ---: | ---: |
| Produccion backend | 0,65 | 2560 MiB |
| Produccion PostgreSQL | 0,30 | 1536 MiB |
| Produccion web | 0,04 | 128 MiB |
| Staging backend | 0,20 | 1536 MiB |
| Staging PostgreSQL | 0,10 | 768 MiB |
| Staging web | 0,03 | 128 MiB |
| Edge | 0,08 | 256 MiB |
| **Total** | **1,40 vCPU** | **6912 MiB / 6,75 GiB** |

Quedan 0,60 vCPU y unos 2,97 GiB fuera de esos techos para el host y
mantenimiento. Son limites, no consumo real ni reservas garantizadas.
Staging arranca mas despacio por su cuota de CPU. Compilaciones y generadores
de carga permanecen fuera de esta VM.

No se cambiaron DNS, reglas de Google ni servicios/variables/bases de Render.
Render sigue siendo el servicio vigente; esta es una inicializacion privada.
El corte final requiere controlar escrituras y hacer una copia final coordinada.
Faltan dominios/TLS publicos, compatibilidad frontend/CORS para ellos, correo
real, respaldos externos/retencion/alertas y una validacion de negocio/carga
acordada. La modalidad privada y el estado implementado estan **pendientes de
sincronizacion manual con Gaphor**; no se edita el modelo en esta entrega.


## Revisión de Render para usar producción como origen — 4 de noviembre

Consultas realizadas el **4 de noviembre de 2026** mediante Render
MCP, exclusivamente en modo lectura. No se redesplegaron servicios, modificaron
variables de Render ni escribieron datos o historial de sus bases.

### Revisiones desplegadas y migraciones

| Componente | Producción | Staging |
| --- | --- | --- |
| Backend activo | `80296d2995d4a8053601f089a17d7df0f6ddd9f4` | `80296d2995d4a8053601f089a17d7df0f6ddd9f4` |
| Frontend activo | `9a3d63fda421d0dce59cd48c7b81f940207e3d94` | `9a3d63fda421d0dce59cd48c7b81f940207e3d94` |
| PostgreSQL | 18.3 | 18.3 |
| Tablas en `public`, incluido Flyway | 145 | 145 |
| Historial de Flyway | 115 registros, última V118 | 115 registros, última V118 |
| Migraciones SQL exitosas / fallidas | 114 / 0 | 114 / 0 |
| Baseline histórico | Versión 2 | Versión 2 |
| Tamaño observado | 42 882 751 bytes | 39 147 199 bytes |

Los cuatro despliegues activos son `live`. El backend de producción se desplegó
el 29 de octubre y el de staging el 25; los frontends, el 29 y 28 respectivamente.
Las fechas diferentes no implican revisiones diferentes. No hace falta un
redespliegue de Render para alinear estos commits.

Se comparó el historial completo por versión, tipo, script, descripción,
checksum y éxito: sin diferencias. Además se calcularon los CRC32 de las 114
migraciones SQL del commit desplegado según el algoritmo de Flyway **9.22.3**:
todos coinciden con los valores de ambas bases. Esto es una comprobación de
integridad de archivos e historial, no una ejecución de `flyway validate` contra
los servidores ni una prueba funcional de aplicación. Referencias:
[validación Flyway](https://documentation.red-gate.com/fd/validate-277578898.html)
y [algoritmo de la versión 9.22.3](https://raw.githubusercontent.com/flyway/flyway/flyway-9.22.3/flyway-core/src/main/java/org/flywaydb/core/internal/resolver/ChecksumCalculator.java).

### Estructura real comparada

Se compararon inventarios y huellas por objeto sobre los catálogos, excluyendo
propietarios, ACL, OID y valores actuales de secuencias. En ambos se observaron
un esquema de aplicación, 145 tablas, 1447 columnas, 1632 restricciones,
414 índices, 123 secuencias, 32 funciones y un trigger de usuario. Las dos
extensiones son `pg_trgm` 1.6 y `plpgsql` 1.0; sus funciones están incluidas
en el recuento de 32. No se observaron vistas, políticas RLS, enums ni dominios
de usuario en ese inventario.

Las relaciones, índices, secuencias, funciones, trigger, esquemas y extensiones
coinciden en las huellas comparadas. Se examinaron las diferencias de columnas
y restricciones:

- Diez columnas de `productos` tienen posiciones físicas diferentes; sus nombres,
  tipos, nulabilidad, valores por defecto, identidad, generación y collation
  coinciden. El origen tiene un hueco ordinal distinto, sin columnas adicionales.
- Veintidós restricciones CHECK difieren en la representación del cast de
  arrays: producción convierte el array de varchar a text[] y staging convierte
  sus literales a text. Coinciden las expresiones restantes, valores admitidos,
  nombres, tipos y estado de validación. Tras normalizar exclusivamente esas
  conversiones, no quedan diferencias entre las definiciones examinadas.

No se identificó un bloqueo de esquema para clonar producción a dos destinos
nuevos usando el commit actual y la línea histórica. Esta conclusión no equivale
a afirmar identidad binaria de los esquemas ni sustituye la restauración de
prueba, la validación de permisos del nuevo rol y el arranque Flyway/Hibernate.

El destino PostgreSQL de la VM se consultó en modo lectura: **18.6**; dispone
de `pg_trgm` **1.6** para instalar durante la restauración y de `plpgsql` 1.0
ya instalado. No se instalaron extensiones ni restauraron datos en esta revisión.

### Diferencia de contenido observada

Solo se consultaron conteos agregados, sin leer registros personales ni documentos:

| Tabla | Producción | Staging |
| --- | ---: | ---: |
| `users` | 26 | 27 |
| `productos` | 838 | 800 |
| `proveedores` | 32 | 29 |
| `ordenes_produccion` | 1510 | 832 |
| `lote` | 3059 | 2029 |
| `movimientos` | 7313 | 5192 |

Tener el mismo código e historial no implica tener los mismos datos. Según la
decisión del usuario, el origen de ambos destinos será producción, sin mezclar
estos conjuntos con el contenido actual de staging de Render.

### Consolidación V1 local y ruta recomendada

Se detectó trabajo local aún sin commit en `application.yml`,
`FlywayConsolidatedConfig.java`, `db/migration-v1/`, `db/bootstrap-v1/` y sus
documentos. No se modifica ni se incluye automáticamente en la imagen ya
preparada: esta procede del commit desplegado `80296d2`.

El manifiesto de la V1 registra 138 tablas capturadas de un PostgreSQL local
18.1 y declara pendiente su equivalencia con Render. Comparar los nombres
confirma que Render contiene seis tablas adicionales, sin contar Flyway:

- `activo_produccion` y `categoria_activo`.
- `ordenes_seguimiento` y `recurso_asignado_orden`.
- `fix_bombonera_frag_color_backup_20260703` y
  `fix_bombonera_gr002_backup_20260703`.

La V1 tampoco declara `pg_trgm`; su manifiesto solo registra `plpgsql`.
No se deduce que las tablas adicionales deban borrarse ni que sus datos sean
prescindibles. La V1 no reproduce íntegramente el origen que el usuario quiere
conservar, por lo que combinarla ahora con una restauración `data-only` requiere
una revisión adicional del inventario y del procedimiento.

**Ruta recomendada para el primer traslado:** conservar el commit actual y
restaurar un respaldo completo de producción —estructura, datos, secuencias e
historial histórico— en cada base nueva de la VM, con roles propios y volúmenes
independientes. Copiar también `/app/data` de producción con una ventana de
consistencia coordinada. La consolidación V1 queda como trabajo separado hasta
comprobar su equivalencia y su estrategia de conservación de datos.

`pg_dump` permite obtener una instantánea consistente de la base mientras está
en uso; no incluye los archivos externos de `/app/data`. Su coherencia conjunta
y el corte definitivo requieren un procedimiento coordinado. Una instantánea
para probar no incorpora automáticamente las escrituras posteriores de Render.
Usar el mismo respaldo para inicializar los dos destinos permite que partan del
mismo punto; a partir de ahí evolucionan de forma independiente.
[Referencia de PostgreSQL 18](https://www.postgresql.org/docs/18/app-pgdump.html).

Esta revisión no sustituye un ensayo de restauración y recuperación ni autoriza
un cambio de DNS o el retiro de Render. La topología modelada se mantiene;
no se modifica Gaphor ni el código fuente durante esta inspección.
