# Acceso adicional por IP: produccion y pruebas

Solicitud del 5 de noviembre de 2026. Se conserva el acceso por subdominios y
SSH; se agrega acceso HTTPS por rutas en la misma IP y los mismos siete
contenedores. La emision de un certificado IP no requiere cambiar DNS.

| Ambiente | Web | Base API adicional |
| --- | --- | --- |
| Produccion | `https://34.30.31.30/prod/` | `https://34.30.31.30/prod/backend` |
| Pruebas | `https://34.30.31.30/staging/` | `https://34.30.31.30/staging/backend` |

## Mensaje para el propietario del dominio

En la zona **exotic.com.co**, crear los siguientes registros de tipo **A**, con
TTL **300**, una vez confirmada la reserva estatica de la IP con el
administrador de Google Cloud:

| Nombre relativo | Destino |
| --- | --- |
| `mrp.prod` | `34.30.31.30` |
| `mrp.staging` | `34.30.31.30` |
| `mrp.api.prod` | `34.30.31.30` |
| `mrp.api.staging` | `34.30.31.30` |

Si el panel completa automaticamente exotic.com.co, usar solo los nombres
relativos de la tabla. Configurar como solo DNS, sin proxy/CDN, y sin registros
AAAA nuevos. Conservar nameservers, correo, dominio raiz y otros registros.
Los certificados los gestiona Caddy en la VM. El propietario no necesita
instalar certificados ni configurar las rutas /prod y /staging en DNS.

La reserva estatica sigue pendiente de confirmacion por el administrador de
`cobalt-duality-407814`, region `us-central1`, VM `vm-produccion`. La consulta
desde la cuenta de servicio no tiene scopes Compute suficientes; esto no
permite determinar si ya hay una reserva. No sustituir la IP ni reiniciar la
VM para comprobarlo. Detalle: [SUBDOMINIOS.md](SUBDOMINIOS.md).

## Funcionamiento

Cada web monta un tercer artefacto, solo lectura, en `/srv-ip`. La seleccion
por `IP_FRONTEND_HOST=34.30.31.30` utiliza un mapa fijo. El edge elimina
exclusivamente `/prod` o `/staging` para servir la web y exclusivamente
`/prod/backend` o `/staging/backend` para reenviar a Spring. Todos los prefijos
originales del backend se conservan, incluidos /api, /productos y los demas.

Los builds IP usan Vite `--base=/prod/` o `--base=/staging/`, Router con basename
y `VITE_API_BASE_URL` que incluye el prefijo backend de la tabla. Las claves
de token, eventos de logout y contexto de sesion se separan por ruta base.
Se conservan las claves anteriores en los builds de raiz usados por
subdominios, Render y SSH.

Los dos ambientes por IP comparten origen del navegador. Los namespaces
evitan colisiones accidentales de sesiones; no constituyen una frontera de
seguridad entre aplicaciones. Los subdominios separados siguen siendo el
acceso definitivo previsto. Las bases y secretos JWT permanecen separados.

Las peticiones a la API de la propia ruta son del mismo origen HTTPS que su
web; no necesitan ampliar CORS. Se conserva la lista de cada backend para
su subdominio y localhost. No cambia el codigo Java, los puertos de Spring o
PostgreSQL, ni los datos.

## HTTPS y configuracion

Caddy gestiona un certificado publico de la IP mediante el perfil ACME
`shortlived` de Let's Encrypt, configurado solo en el bloque IP. Su validez
es de 160 horas; Caddy debe permanecer operativo y conservar `/data` para
renovarlo. Los cuatro dominios mantienen sus emisores normales. Referencias:
[Let's Encrypt: certificados IP](https://letsencrypt.org/2026/01/15/6day-and-ip-general-availability/)
y [Caddy: emisor ACME](https://github.com/caddyserver/caddy/blob/v2.11.7/modules/caddytls/acmeissuer.go).

`default_sni` selecciona el certificado IP cuando el cliente no envia SNI y el
servidor recibe una direccion interna de Docker. Se retira `strict_sni_host on`
global para permitir esos clientes; se usa el comportamiento estandar de
Caddy con hosts explicitos. Los listeners SSH siguen en loopback y puertos
distintos; no se exponen en las rutas publicas. No se agregan VPN, WAF ni
servicios permanentes adicionales.

Archivos de configuracion:

- `config/sites/ip.caddy.example`: se activa como
  `/srv/exotic/private/edge/sites/ip.caddy`.
- `env/edge.env.example`: `VM_PUBLIC_IP` y los cuatro nombres.
- `env/production.env.example` y `env/staging.env.example`:
  `IP_FRONTEND_HOST` y `IP_FRONTEND_DIST_DIR`.
- Frontend `env-examples/.env.ip-production.example` y
  `env-examples/.env.ip-staging.example`: valores publicos de compilacion,
  comentarios de uso y comandos, nunca secretos.

El sufijo `.example` y la carpeta `env-examples/` no se cargan automaticamente.
Desde la raiz del repositorio frontend, Bun puede cargar el ejemplo elegido
explicitamente para la compilacion. Construir fuera de la VM:

```bash
bun --env-file=./env-examples/.env.ip-production.example run vite build --base=/prod/ --outDir /ruta/artefactos/dist-ip-production
bun --env-file=./env-examples/.env.ip-staging.example run vite build --mode staging --base=/staging/ --outDir /ruta/artefactos/dist-ip-staging
```

No reutilizar el mismo dist entre estas dos rutas ni como artefacto de raiz.
Los limites se conservan: 1,40 vCPU y 6912 MiB entre siete contenedores.
Actualizar solo frontend requiere recrear solo web; este cambio no requiere
reiniciar backend o PostgreSQL.

## Verificacion y recuperacion

La comprobacion debe usar HTTPS sin omitir validacion del certificado:

```powershell
curl.exe -I https://34.30.31.30/prod/
curl.exe -I https://34.30.31.30/staging/
curl.exe -i https://34.30.31.30/prod/backend/api/auth/me
curl.exe -i https://34.30.31.30/staging/backend/api/auth/me
```

Comprobar navegador, assets bajo su prefijo, rutas de login/retorno, API,
sesiones separadas y rechazo de JWT del otro ambiente. El acceso por IP no
acredita los registros DNS ni los certificados de los subdominios.

Antes de aplicar se guardo la configuracion vigente y el inventario de
contenedores en `/srv/exotic/private/ip-paths-20261105/`, modo 0700. Sus copias
privadas permiten recuperar la configuracion anterior y recrear solo webs y
edge. No ejecutar un rollback del esquema ni restaurar bases por un problema
de routing. No se ha modificado Render ni se ha realizado el corte de datos.

## Resultado aplicado

Configuracion aplicada el **5 de noviembre de 2026**. Verificacion externa a
las **19:48:11 UTC / 14:48:11 Colombia**; verificacion de API y contenedores
a las **19:48:48 UTC / 14:48:48 Colombia**.

- Certificado publico de IP validado desde Windows con el almacen de CA del
  sistema, sin `-k`, excepciones ni CA privada. SAN `IP Address:34.30.31.30`.
  Vigencia observada: 5 de noviembre 18:49:14 UTC a 12 de noviembre
  10:49:13 UTC. La renovacion automatica queda a cargo de Caddy.
- `/prod/`, `/staging/` y sus rutas de login: HTTP 200. La raiz IP responde
  404 e indica las dos rutas; HTTP redirige a HTTPS. No se publica login por HTTP.
- Los 15 recursos de entrada de cada frontend respondieron 200 bajo su propio
  prefijo. Assets inexistentes conservan 404 y las rutas SPA reciben su shell.
- Navegador: produccion redirige a `/prod/login`, titulo Exotic; staging a
  `/staging/login`, titulo Exotic (Pruebas) y etiqueta ENTORNO DE PRUEBAS.
  Ambos logos cargan y no se registraron errores de consola en estas pantallas.
- API de cada ruta: lectura autenticada de `/api/auth/me` y
  `/productos/unidades-medida` con HTTP 200; consulta sin JWT con HTTP 401.
  Los JWT del otro entorno se rechazan con 401. La peticion del mismo origen
  IP funciona sin cambiar CORS.
- Se comprobaron tambien los artefactos de subdominios y SSH. Los cuatro
  nombres y sus certificados publicos siguen dependiendo del DNS pendiente.
- Solo se recrearon las dos webs y edge. Los cuatro contenedores de backend
  y PostgreSQL conservaron sus IDs y horas de arranque; sin reinicios. Los
  seis servicios de aplicacion estan saludables y edge operativo.
- Historial completo Flyway identico antes y despues en ambas bases, 115
  filas por entorno. No se restauraron datos ni se modifico codigo Java,
  migraciones o configuracion privada del backend.
- Siete contenedores; mismos limites totales de 1,40 vCPU y 6912 MiB.

Release frontend: `/srv/exotic/releases/20261105-ip-paths-fe9a3d63f`, del commit
`9a3d63f` mas los cambios de configuracion/rutas/sesiones documentados. Su
`release-manifest.json` registra hashes de cada archivo modificado. SHA256 del
archivo transferido `frontend-artifacts.tar.gz`:
`6024404bfc15a0a2e2e71e31466dbac1eab091d200bcd47481b0da839de2709b`.
El backend mantiene `exotic-backend:vm-domains-20261105-be80296d2`.

Validaciones locales: cinco `bun run vite build` pasaron, con advertencias de
tamano de chunks; 29 comprobaciones de configuracion/rutas/sesion pasaron.
`bun run lint` falla tanto en el commit limpio como en la copia modificada,
con salida identica por `DispensacionV2Step3SeleccionOrdenes.tsx:65` y
supresiones sin uso. No se alteraron supresiones ni se ejecutaron suites.
Caddy validate y Compose config pasaron. La entrada del usuario con su
contrasena y los flujos completos de negocio permanecen para validacion manual.

Evidencia remota privada: `verification.json` y `before.json` en
`/srv/exotic/private/ip-paths-20261105/`. La comprobacion TLS externa y la del
navegador se resumen aqui; no incluyen credenciales de usuario. Los JWT de
smoke fueron de vida corta y solo estuvieron en memoria.

Render sigue vigente y no se han sincronizado escrituras posteriores a la
copia inicial. El acceso publico de estas copias no constituye un corte de
produccion. Backup remoto y reserva estatica confirmada siguen pendientes.
El diagrama `deployment migracion` queda pendiente de sincronizacion manual
para anadir estas rutas y el tercer artefacto por web; no se modifica Gaphor.

## Indicador temporal de produccion

Por solicitud del usuario se amplio
`exotic-app-frontend/src/components/EnvironmentBadge.tsx`, conservando su
ubicacion inferior derecha y los textos LOCAL DEV y ENTORNO DE PRUEBAS.
Produccion muestra un badge rojo: PRODUCCION: RENDER o PRODUCCION: GCLOUD.
Se identifica el destino de la API configurada mediante hosts exactos, sin
consultas de red; no se presenta esta etiqueta como una comprobacion del
servidor ni se modifica el entorno real, permisos, sesiones o endpoints.
Un proveedor desconocido muestra solamente PRODUCCION. El dist SSH sigue
clasificandose como local.

Release de esta actualizacion: `/srv/exotic/releases/20261105-production-badge-fe9a3d63f`.
Es la release anterior mas exclusivamente este componente; los cambios
locales de otros modulos se excluyeron. Se recrearon solo ambas webs; backend,
PostgreSQL y edge conservaron sus contenedores y horas de arranque.
Comprobacion remota: **5 de noviembre de 2026, 20:06:39 UTC / 15:06:39 Colombia**.
Los seis servicios de aplicacion continuan saludables. Navegador: login de
`/prod/` muestra PRODUCCION: GCLOUD y staging conserva ENTORNO DE PRUEBAS;
sin errores de consola en la pantalla productiva.

Los cinco builds VM y un build limpio compatible con Render pasaron.
`bun run lint` conserva el mismo fallo previo, con salida identica antes y
despues del componente; no se ejecutaron suites de pruebas. SHA256 del
componente: `0a0a4cf4d229884dff03857d2e436823ece8b5d1297c0e470e3ff57f5e6fd69e`.
Evidencia privada: `/srv/exotic/private/production-badge-20261105/verification.json`.

El cambio para Render esta preparado sobre su commit vigente `9a3d63f`,
modificando unicamente el badge. Su publicacion en GitHub y despliegue del
frontend de produccion de Render estan pendientes de confirmacion explicita.
Render produccion tiene autodeploy desactivado; staging sigue main y se
actualizaria automaticamente al publicar el commit. No se modificaron aun
servicios ni codigo remoto de Render/GitHub por este indicador.

Este componente no esta representado en el modelo y el indicador no cambia
la arquitectura de despliegue: no requiere un nuevo diagrama ni modificaciones
adicionales de Gaphor. Permanecen las sincronizaciones anteriores pendientes.

### Ampliacion del indicador a staging

Actualizado tambien el badge de pruebas: **PRUEBAS: RENDER** o
**PRUEBAS: GCLOUD**, segun la misma identificacion exacta de API. Se conserva
el color naranja; produccion y local mantienen sus textos y colores.
Un proveedor desconocido en staging muestra PRUEBAS, sin atribuir plataforma.

Staging VM usa `/srv/exotic/releases/20261105-staging-badge-fe9a3d63f`;
produccion conserva su release anterior. Se recreo exclusivamente
`exotic-staging-web-1`. Produccion, backends, bases y edge mantuvieron sus
contenedores. Comprobado el **5 de noviembre de 2026 a las 22:06:17 UTC /
17:06:17 Colombia**: seis servicios saludables y bundle staging accesible.
El navegador confirma PRUEBAS: GCLOUD en `/staging/login`, sin errores de consola.

Pasaron cinco builds Vite: SSH, staging por dominio, staging por IP,
comprobacion de produccion por IP y build limpio compatible con Render.
El lint conserva salida identica al estado anterior por el fallo previo;
no se ejecutaron suites. SHA256 del componente actualizado:
`b03be3831676ef9c4c5efd77f59e9010a10e4ddf6fb96d17b425eaa2e7a172d2`.
Evidencia privada: `/srv/exotic/private/staging-badge-20261105/verification.json`.

La publicacion pendiente de Render incluye ahora ambos indicadores en el
mismo componente y futuro commit aislado. Esta ampliacion no constituye
confirmacion para publicar ni desplegar Render. Los cambios locales ajenos
se preservaron y se excluyeron de la release. No cambia Gaphor.
