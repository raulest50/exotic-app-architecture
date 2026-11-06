# Compatibilidad de Exotic: cambios aplicados y verificaciones pendientes

Revision inicial: **4 de noviembre de 2026**; actualizada el **5 de noviembre**.
Ambos entornos ya estan activos en la VM. Se implementaron seleccion explicita
de API/entorno en frontend y CORS configurable en backend para los cuatro
subdominios acordados. La evidencia y la entrega DNS estan en
[SUBDOMINIOS.md](SUBDOMINIOS.md); el origen de los datos y la restauracion, en
[DESPLIEGUE_INICIAL.md](DESPLIEGUE_INICIAL.md).

Los ejemplos mantienen `APP_COMPATIBILITY_CONFIRMED=false`. El operador no debe
cambiarlo a `true` hasta completar y registrar las comprobaciones publicas y
los requisitos operativos pendientes. Es una comprobación de `stack.sh`, no
una protección de red. El arranque actual usa `pilot.sh` y el edge se administra
aparte; los listeners publicos 80/443 ya estan configurados.

## Frontend: selección de API y artefacto estático

En `exotic-app-frontend/src/api/EndPointsURL.tsx`, `getDomain()` y
`getEnvironment()` comparten un resolver. Si se configura cualquiera de
`VITE_API_BASE_URL` o `VITE_APP_ENV`, ambas son obligatorias. La URL debe ser
una URL base HTTPS, opcionalmente con prefijo de ruta y sin credenciales,
query ni fragmento; HTTP solo se acepta
para localhost/127.0.0.1. El entorno admite local, staging o production.
Sin variables se conservan fallbacks para localhost y los dos hostnames exactos
actuales de Render. Un host desconocido produce un error, sin seleccionar
produccion por defecto. Las plantillas del frontend
`env-examples/.env.staging.example` y `env-examples/.env.production.example`
solo contienen valores publicos y comentarios de uso. No se cargan
automaticamente; se pasan explicitamente al comando Bun con `--env-file`.

Establecer una variable en Compose no cambia el JavaScript ya compilado. Las
variables `VITE_` se fijaron al construir cada artefacto fuera de la VM.
El acceso IP agrega builds con `--base=/prod/` y `--base=/staging/`, Router
basename y claves de sesion por ruta. Su API usa el prefijo correspondiente
`/prod/backend` o `/staging/backend`, conservando todos los endpoints actuales.

La propuesta usa **un dominio web y un dominio API distintos por entorno**.
`PUBLIC_DOMAIN` identifica la web y `API_PUBLIC_DOMAIN` su API. El proxy común
recibe `STAGING_WEB_DOMAIN`, `STAGING_API_DOMAIN`, `PRODUCTION_WEB_DOMAIN` y
`PRODUCTION_API_DOMAIN`. La URL elegida al construir el frontend debe coincidir
con la API del mismo entorno; no basta con que ambos nombres contengan la
palabra `staging`.

El dominio API reenvía la URI completa al backend. Los contratos existentes
mezclan `/api/...`, `/productos`, `/categorias`, `/compras`, `/usuarios` y
`/bi/...`, entre otras rutas. No añadir un prefijo `/api` universal ni retirarlo
de las rutas que ya lo contienen. En particular, `handle_path /api/*` eliminaría
ese prefijo en Caddy; esta semántica está descrita en su
[documentación oficial](https://caddyserver.com/docs/caddyfile/directives/handle_path).
La separación de dominios evita confundir rutas de API con el fallback de la SPA.

El servicio `web` sirve archivos **precompilados fuera de la VM**, mediante
Caddy en el puerto interno `8080`. `FRONTEND_DIST_DIR` monta el artefacto SSH
en `/srv`; `PUBLIC_FRONTEND_DIST_DIR` monta el publico en `/srv-public`, ambos
solo lectura. Un mapa fijo por `PUBLIC_FRONTEND_HOST` selecciona el segundo;
los demas hosts reciben el primero. No se construyen rutas desde Host. Se
comprobaron los assets y la referencia API real de cada build publico; la
verificacion del navegador sobre DNS/HTTPS publico queda pendiente.
El tercer montaje `/srv-ip` sirve el artefacto por ruta cuando Host coincide
con `IP_FRONTEND_HOST`. La configuracion y evidencia de este acceso estan en
[ACCESO_IP.md](ACCESO_IP.md); no modifica las listas CORS de los backends.

La base local acordada es Bun **1.3.14**, `bun.lock` y el build de Vite usado
por Render. El `Dockerfile` actual del frontend usa `oven/bun:1`, copia
`bun.lockb`, ejecuta `bun test` y `bun run build`; este último ejecuta TypeScript
y Vite, y no equivale al build de Render. Por tanto, ese Dockerfile no es el
artefacto de publicación definido aquí. No ejecutar ni corregir automáticamente
ese flujo como parte de la preparación de infraestructura. Para construir el
`dist`, seguir las instrucciones de `exotic-app-frontend/AGENTS.md`,
incluido el uso exclusivo de Bun y su lockfile autoritativo.

## Backend: imagen externa, CORS y proxy

La imagen del backend debe construirse fuera de la VM desde una revisión
conocida y publicarse con una versión identificable; preferir una referencia
por digest al promover exactamente el artefacto revisado. Compose descarga y
ejecuta esa imagen: no compila el repositorio en producción.

**No construir una imagen desde el workspace local que contiene secretos.**
El Dockerfile actual copia `src` y `.dockerignore` no excluye
`application*.properties`; la exclusión de Git no los excluye del contexto de
Docker. La construcción futura debe partir de un checkout limpio y un contexto
revisado, sin esos archivos. No copiar, leer, empaquetar ni trasladar sus valores
a esta propuesta. Verificar también el JAR y las capas antes de publicar; una
imagen ya contaminada debe sustituirse por un artefacto limpio.

`exotic-app-backend/src/main/java/exotic/app/planta/config/CorsConfig.java`
lee `app.cors.allowed-origins`. Si existe, su CSV de origenes exactos reemplaza
la lista completa de defaults; rechaza listas vacias, wildcards, rutas,
credenciales y otras formas invalidas. Si falta, conserva los seis origenes
localhost/Render previos. En la VM cada `backend.properties` privado contiene
solo su web HTTPS, `http://localhost:5173` y `http://localhost:3000`. Se
comprobo preflight permitido para esos origenes y rechazado para el otro
ambiente y origenes desconocidos.

La propuesta establece `SERVER_FORWARD_HEADERS_STRATEGY=framework` para que
Spring procese la información de la conexión exterior transmitida por el proxy;
no añade por sí misma orígenes CORS. El backend debe quedar accesible únicamente
por las redes previstas y el proxy debe controlar las cabeceras reenviadas.
Validar CORS, preflight, autenticación y respuestas reales desde el nuevo origen
web antes de confirmar compatibilidad. La propiedad de cabeceras está descrita
en [Spring Boot 3.2.5: ejecución detrás de un proxy](https://docs.spring.io/spring-boot/docs/3.2.5/reference/html/howto.html#howto.webserver.use-behind-a-proxy-server).

## Configuración externa y secretos

Spring Boot es **3.2.5** y Java **21** según el repositorio. Revisar las
propiedades requeridas por la revisión exacta del backend; DB y JWT no son
necesariamente su única configuración. Las integraciones de correo, servicios
externos y almacenamiento deben inventariarse por nombre de propiedad, sin
recuperar sus valores de los archivos privados locales.

| Dato | Destino previsto | Comprobación requerida |
| --- | --- | --- |
| Servidor PostgreSQL | `DB_HOST=database`, `DB_PORT=5432` | Resolución dentro de la red del entorno; sin publicar PostgreSQL a Internet. |
| Base y usuario de aplicación | `DB_NAME`, `DB_USER` | Coincidir con base, rol y privilegios restaurados de ese entorno; no usar el usuario administrador para el backend. |
| Contraseña de aplicación | Archivo secreto montado como `/run/secrets/DB_PASSWORD` | El nombre del archivo expone la propiedad `DB_PASSWORD` mediante `configtree`; coincidir con la contraseña del rol PostgreSQL. |
| Secreto JWT | Archivo secreto montado como `/run/secrets/jwt.secret` | Exponer `jwt.secret` mediante `configtree`; no aceptar el valor por defecto del código. |
| Otras propiedades privadas | `/run/secrets/backend.properties` | Archivo nuevo preparado por el operador para cada entorno e importado explícitamente; fuera del repositorio. |

El contrato de importación es
`SPRING_CONFIG_IMPORT=file:/run/secrets/backend.properties,configtree:/run/secrets/`.
Un árbol de configuración interpreta nombres de archivos como nombres de
propiedades; un archivo `.properties` completo se importa por separado para
interpretar sus pares clave-valor. En esta propuesta las ubicaciones son
obligatorias: si faltan, no deben ocultarse con `optional:`. Véase
[Spring Boot 3.2.5: importación y árboles de configuración](https://docs.spring.io/spring-boot/docs/3.2.5/reference/html/features.html#features.external-config.files.configtree).

Los secretos se suministran como archivos y Compose concede acceso solo a los
servicios declarados. Esto **no cifra los archivos del host**: requieren permisos
y custodia adecuados. No incluirlos en el repositorio, en un `.env` versionado,
en una imagen o en una salida de diagnóstico. La entrega mediante archivos y
la convención `_FILE` de algunas imágenes están descritas en
[Docker Compose: secretos](https://docs.docker.com/compose/how-tos/use-secrets/).
Esta documentación no contiene secretos. Los actuales se generaron en la VM
durante la inicializacion anterior y no proceden de archivos privados locales.

## Entorno de ejecución explícito

`ApplicationRuntimeEnvironmentResolver.java` admite la propiedad
`app.runtime-environment`. En ausencia de una selección explícita u otra señal
admitida, un hostname fuera de Render puede terminar clasificado como `LOCAL`.
Esto afecta decisiones de la aplicación, incluida la disponibilidad de
información de diagnóstico: no es solo una etiqueta visual.

Cada entorno debe recibir explícitamente `APP_RUNTIME_ENVIRONMENT=production`
o `APP_RUNTIME_ENVIRONMENT=staging`, de acuerdo con su función, y comprobarse
con el artefacto real. No utilizar `PRODUCTION=true` para ambos ni asumir que el
nombre del proyecto Compose sustituye esta propiedad. Los ejemplos usan el
entorno elegido por el operador y el procedimiento debe rechazar valores
inconsistentes.

## Restauración, Flyway y Hibernate

Mantener **Flyway habilitado** y **Hibernate en validación** en ambos entornos:
`SPRING_FLYWAY_ENABLED=true` y `SPRING_JPA_HIBERNATE_DDL_AUTO=validate`.
No desactivar migraciones ni usar `update`, `create`, `create-drop` o `none`
para eludir un fallo.

Antes del primer arranque del backend, restaurar y comprobar la base del entorno,
incluido su historial Flyway, roles, propiedad de objetos y compatibilidad con
la revisión elegida. Restaurar también los documentos asociados y comprobar su
correspondencia con los registros. No arrancar una aplicación con migraciones
contra una base vacía o equivocada para luego intentar reemplazarla por el dump.

Flyway puede aplicar migraciones al arrancar. Resolver previamente las
migraciones pendientes y su procedimiento de reversión/recuperación; volver a
una imagen anterior no revierte automáticamente el esquema. Usar el plan de
[recuperación](RECUPERACION.md) antes de autorizar cualquier operación real.

## Salud, validación y automatización pendiente

No se verificó un Actuator instalado y publicado ni un endpoint contractual de
salud apto para producción. No inventar `/actuator/health`, no usar endpoints de
negocio como sondas y no habilitar `/api/backend-info/**` en producción para
obtener una comprobación fácil. Un contenedor iniciado, un socket abierto o un
`401` solo acreditan aspectos limitados; no demuestran que una operación de
negocio, la base y el almacenamiento funcionen correctamente.

El workflow actual del backend escucha `master` y compila con `-x test`; no es
una red de seguridad para la rama de trabajo `main`. La futura CI deberá
definirse y autorizarse por separado. En esta entrega no se ejecutaron suites
de pruebas de la aplicación. Las pruebas unitarias e integración y
los ejecutores E2E deben planificarse fuera de los recursos de producción;
staging sigue siendo el destino estable para las comprobaciones que lo requieran.

Antes de retirar Render, registrar como mínimo:

1. Revisiones exactas del frontend y backend, digest de imagen y procedencia del
   `dist`, construidos sin secretos locales.
2. API seleccionada por el frontend, CORS desde cada origen nuevo, autenticación,
   conservación de las rutas con y sin `/api`, navegación SPA y cabeceras HTTPS.
3. Clasificación explícita del entorno y aislamiento de datos, credenciales,
   redes y volúmenes entre producción y staging.
4. Restauración comprobada de DB y documentos antes del arranque, validación de
   Flyway/Hibernate y prueba de recuperación con el procedimiento aprobado.
5. Comprobaciones de aplicación acordadas, límites de capacidad bajo carga real,
   criterios de reversión y registro del responsable que confirma compatibilidad.

Hasta entonces conservar `APP_COMPATIBILITY_CONFIRMED=false`. La configuracion
actual fue desplegada por solicitud del usuario; el cambio de DNS corresponde
al propietario del dominio y no se ha hecho un corte ni apagado Render.

## Evidencia de la actualizacion del 5 de noviembre

Gradle `build -x test -Pprod` y los tres builds Vite completaron. El lint del
frontend falla por un problema previo en
`DispensacionV2Step3SeleccionOrdenes.tsx:65`; su salida es identica con y sin
este cambio. No se modifico ese archivo ni se afirma que el gate haya pasado.

La release usa los commits estables del despliegue anterior y solo los cambios
de CORS y los dos archivos de configuracion frontend. No incorpora trabajo
local de consolidacion V1. El JAR no contiene propiedades privadas y conserva
los 116 archivos de migraciones historicas sin cambios. El historial de ambas
bases permanece igual tras actualizar los backends.

Pasaron Caddy/Compose, lecturas autenticadas, aislamiento JWT entre entornos
y routing TLS de los cuatro nombres mediante una CA temporal aislada. Esta
ultima comprobacion no valida ACME ni DNS publico. Se mantienen pendientes
DNS, certificados publicos, reserva de IP por confirmar, login manual, carga,
backup remoto y corte coordinado desde Render. Detalle: SUBDOMINIOS.md.

## Ejecución desde Windows y Linux

PowerShell puede copiar estos archivos y consultar su contenido. Si dispone de
Docker Compose, puede validar el modelo con `docker compose ... config --quiet`
usando los archivos y variables de ejemplo adecuados; esa validación no inicia
servicios ni comprueba que los paths Linux existan en la VM. Evitar imprimir la
configuración interpolada con valores reales o copiar secretos para validarla.

Los scripts de `scripts/` y `postgres/init-app-user.sh` son **Bash para Linux**.
Su análisis sintáctico puede hacerse en Debian de WSL sin ejecutarlos; su uso
operativo requiere Linux y el contexto del Docker Engine del servidor objetivo.
No ejecutarlos con Windows CMD o como instrucciones PowerShell. WSL y Debian
de la VM son sistemas distintos: el Docker Desktop local integrado con WSL no
debe confundirse con el Docker Engine de la VM ni seleccionarse como destino
accidental de comandos de despliegue. No se instala ninguna herramienta en esta
entrega.

## Evidencia local consultada

Rutas relativas al workspace `exotic_ws`:

- `exotic-app-frontend/AGENTS.md`, `.bun-version`, `.node-version`,
  `package.json`, `Dockerfile` y `src/api/EndPointsURL.tsx`.
- `exotic-app-backend/AGENTS.md`, `Dockerfile`, `.dockerignore`,
  `build.gradle.kts`, `.github/workflows/gradle-build.yml` y
  `src/main/resources/application.yml`.
- `exotic-app-backend/src/main/java/exotic/app/planta/config/CorsConfig.java`,
  `config/SecurityConfig.java`,
  `config/runtime/ApplicationRuntimeEnvironmentResolver.java`,
  `security/JwtTokenProvider.java` y mappings de `resource/`.
- `ssh_gcloud/CAPACIDADES_VM.md` y el diagrama `Despliegue` del modelo.

No se leyeron ni empaquetaron los `application*.properties` locales. La revision
inicial fue documental; la actualizacion del 5 de noviembre incluye las
comprobaciones remotas descritas, sin publicar valores secretos.
