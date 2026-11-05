# Subdominios de la VM: preparacion y entrega de DNS

Solicitud del 5 de noviembre de 2026. Alcance: dejar preparada la VM y las
aplicaciones con lo minimo esencial: HTTPS, CORS exacto y solo Caddy como
entrada web publica. Se conservan los siete contenedores, sus limites y los
volumenes de datos. No se agregan WAF, VPN ni autenticacion adicional.

## Nombres acordados

| Entorno | Web | API |
| --- | --- | --- |
| Produccion | `mrp.prod.exotic.com.co` | `mrp.api.prod.exotic.com.co` |
| Pruebas | `mrp.staging.exotic.com.co` | `mrp.api.staging.exotic.com.co` |

El orden de la API es **mrp.api.prod** y **mrp.api.staging**. No utilizar
`api.mrp.*`, `stating` ni el sufijo `exotic.com.com`.

## Estado y dependencias

La IP externa observada el 5 de noviembre es **34.30.31.30**. Todavia debe
confirmarse en Google Cloud si esta reservada como estatica. El acceso SSH
permite administrar la VM, pero no acredita permisos administrativos del
proyecto GCP. La cuenta de servicio disponible tiene scopes de almacenamiento,
logs y monitorizacion, sin Compute; la consulta de direcciones devuelve
`insufficient authentication scopes`. Ese resultado **no prueba** que la IP
sea efimera ni que no exista una reserva.

Antes de entregar definitivamente la IP al administrador DNS, quien administra
el proyecto `cobalt-duality-407814` debe confirmar su reserva o promover la
direccion actual a estatica en `us-central1`. La instancia es `vm-produccion`,
zona `us-central1-b`. No sustituir la IP ni reiniciar la VM para resolverlo.

Los cuatro nombres no resolvian en la comprobacion inicial. Los certificados
publicos solo podran completarse despues de DNS correcto y conectividad.
Los resultados finales de esta preparacion se agregan al final del documento.

## Configuracion de nuestro lado

- `EndPointsURL.tsx` acepta `VITE_APP_ENV` y `VITE_API_BASE_URL`, ambas juntas.
  El entorno es `staging` o `production` y la API la de la tabla. Se conservan
  fallbacks exactos para localhost y las dos webs actuales de Render; un host
  desconocido sin configuracion ya no selecciona produccion silenciosamente.
- Son variables publicas de compilacion. Cambiar un `.env` del servidor no
  cambia un `dist` ya generado. Las plantillas del frontend son
  `.env.staging.example` y `.env.production.example`; nunca poner secretos en
  variables `VITE_`.
- Hay un artefacto para SSH, sin esas variables, y uno publico por entorno.
  Cada web monta `/srv` y `/srv-public` como solo lectura. Caddy usa un mapa
  fijo del hostname `PUBLIC_FRONTEND_HOST` para elegir el artefacto; la
  cabecera Host nunca se utiliza como ruta de archivos.
- El backend lee `app.cors.allowed-origins` de su `backend.properties` privado.
  Cada VM acepta su propia web HTTPS y `http://localhost:5173` y
  `http://localhost:3000` para los tuneles existentes. Sin la propiedad se
  conservan los origenes actuales de localhost/Render. No se usa wildcard.
- El edge publico conserva los cuatro listeners loopback y agrega TCP80/443.
  Los cuatro hosts tienen routing explicito, con todas las URI originales:
  no se agrega ni elimina un prefijo API. Caddy administra HTTPS y redirige
  HTTP a HTTPS. Su API administrativa sigue desactivada.
- PostgreSQL y Spring no publican puertos del host. Bases, documentos,
  credenciales y datos de cada entorno se conservan. SMTP sigue desactivado
  en las copias y Render permanece vigente; este paso no hace un corte de datos.

La release preparada es
`/srv/exotic/releases/20261105-domains-be80296d2-fe9a3d63f`, con backend del
commit `80296d2` mas unicamente el cambio CORS y frontend del commit `9a3d63f`
mas los dos archivos de configuracion. No incorpora los cambios locales V1 ni
otros cambios sin commit. Manifiesto: `release-manifest.json` de esa release.

Mientras DNS esta pendiente, los archivos privados de aplicaciones conservan
`APP_COMPATIBILITY_CONFIRMED=false` y metadata de acceso por localhost. Los
campos `PUBLIC_FRONTEND_HOST` y `PUBLIC_FRONTEND_DIST_DIR` preparan la web
publica sin perder el acceso SSH. El edge se administra por su propio Compose;
estas marcas no son un firewall ni una comprobacion de certificados publicos.
El backup remoto y el corte de produccion son pendientes distintos y no se
declaran resueltos por preparar los dominios.

## Lo que debe hacer el administrador del dominio

Una vez confirmada la IP estatica, crear estos registros en la zona
**exotic.com.co**. Algunos paneles solicitan solo el nombre relativo:

| Tipo | Nombre relativo | Nombre completo | Destino propuesto | TTL |
| --- | --- | --- | --- | --- |
| A | `mrp.prod` | `mrp.prod.exotic.com.co` | `34.30.31.30` | 300 |
| A | `mrp.staging` | `mrp.staging.exotic.com.co` | `34.30.31.30` | 300 |
| A | `mrp.api.prod` | `mrp.api.prod.exotic.com.co` | `34.30.31.30` | 300 |
| A | `mrp.api.staging` | `mrp.api.staging.exotic.com.co` | `34.30.31.30` | 300 |

Crear registros DNS directos, sin agregar un proxy/CDN en esta preparacion.
No se necesita cambiar nameservers ni transferir el dominio. No modificar
registros de correo, la web raiz ni otros subdominios. No crear registros AAAA
para estos nombres porque no se ha preparado una entrada IPv6 externa.
Si ya existen registros incompatibles para estos cuatro nombres, revisarlos
antes de reemplazarlos. Si existen politicas CAA restrictivas heredadas, deben
permitir el emisor ACME usado por Caddy; comprobarlo al emitir certificados.

## Comprobacion despues de DNS

Caddy puede registrar errores ACME antes de que exista DNS. Reintenta
automaticamente, con espera creciente que puede llegar a un dia entre intentos.
Cuando los cuatro nombres apunten a la IP correcta, comprobar conectividad y,
si esta esperando, reiniciar **solo edge** para reintentar:

```bash
cd /srv/exotic/deployment
sudo docker compose --project-directory /srv/exotic/deployment --env-file /srv/exotic/private/edge/edge.env -f compose.edge.yaml restart edge
```

No usar `caddy reload`: la API administrativa esta desactivada. No hace falta
reiniciar backend, frontend ni bases para reintentar la emision.

Desde un equipo externo, verificar sin ignorar certificados:

```powershell
curl.exe -I https://mrp.prod.exotic.com.co/
curl.exe -I https://mrp.staging.exotic.com.co/
curl.exe -i https://mrp.api.prod.exotic.com.co/api/auth/me
curl.exe -i https://mrp.api.staging.exotic.com.co/api/auth/me
```

Las webs deben responder correctamente y las API rechazar la consulta sin
autenticacion. Revisar tambien preflight CORS, login y una lectura autenticada
desde cada web. Las pruebas con resolucion local y una CA efimera validan
routing/configuracion; **no acreditan DNS publico ni certificados ACME**.

Los comandos de tunel existentes estan en
[DESPLIEGUE_INICIAL.md](DESPLIEGUE_INICIAL.md#acceso-privado-desde-windows).
El dist SSH sigue identificandose como local por el hostname; no utilizar esa
etiqueta como acreditacion de que se esta accediendo a una base de desarrollo.

## Gaphor

Se conserva `ExoticApp.gaphor`. Pendiente sincronizar manualmente
`deployment migracion`: los cuatro nombres, CORS configurable, los artefactos
publico/SSH del mismo frontend y la entrada publica preparada junto con
loopback. Se mantienen contenedores, redes, volumenes y presupuesto.

## Validaciones de compilacion

- Gradle Java21 `build -x test -Pprod` dentro de una construccion limpia: paso.
- Vite build de los tres artefactos: paso, con advertencia de chunks grandes.
- Resolver de configuracion: 14 casos de humo, incluidos Render/local,
  valores publicos, configuracion incompleta y hosts desconocidos: paso.
- `bun run lint`: falla tanto en el commit limpio como en la copia modificada,
  con salida identica: `DispensacionV2Step3SeleccionOrdenes.tsx:65`, regla
  `react-hooks/exhaustive-deps`, y supresiones sin uso. No se cambio ese archivo.
- JAR sin configuracion privada ni consolidacion V1; las 116 migraciones
  versionadas mantienen sus hashes. Las 114 aplicadas conservan su historial.
- Validacion nativa de Caddy para edge y web: paso.

No se ejecutaron suites de pruebas de la aplicacion.

## Resultado aplicado y comprobado

Comprobacion final: **5 de noviembre de 2026, 18:23:24 UTC / 13:23:24 Colombia**.

| Componente | Resultado |
| --- | --- |
| Produccion | PostgreSQL, backend y web saludables; cero reinicios |
| Staging | PostgreSQL, backend y web saludables; cero reinicios |
| Edge compartido | Operativo, cero reinicios; TCP80/443 publicos y cuatro puertos SSH en loopback |
| Cuotas efectivas totales | 1,40 vCPU y 6912 MiB; no se incremento el presupuesto |
| Puertos del host de database/backend/web | Ninguno |
| Acceso SSH | Conservado con artefacto frontend que utiliza localhost:8080 |
| DNS de los cuatro nombres | Sin resolucion en la comprobacion final |
| Certificados publicos ACME | Pendientes; no se han acreditado |

Los puertos TCP80 y TCP443 respondieron desde Windows fuera de la VM. HTTP80
con cada uno de los cuatro Host devuelve 308 al HTTPS del mismo nombre. La
redireccion HTTP por IP no entrega contenido de la aplicacion ni constituye
una comprobacion de certificado para la IP.

Los checks privados de cada ambiente validaron web, asset con API correcta,
preflight CORS propio/local permitido y CORS cruzado/desconocido rechazado.
Una lectura autenticada de `/api/auth/me` y `/productos/unidades-medida`
respondio 200; sin JWT, `/api/auth/me` respondio 401. Los JWT de comprobacion
fueron de vida corta, solo en memoria y no requirieron cambiar contrasenas.
El login con contrasena en el navegador queda para comprobacion manual.

La comprobacion TLS termino a las **18:21:35 UTC**. Se utilizo temporalmente
un segundo proceso Caddy dentro del edge, escuchando en 8443 sin publicarlo
en el host, con CA aislada y confianza limitada al cliente de comprobacion.
Verifico SNI/hostname, web, assets, CORS, rutas y lecturas autenticadas de los
cuatro nombres. Los JWT cruzados se rechazaron. El proceso y sus claves
temporales se retiraron; no se instalo esa CA en ningun equipo ni se sustituyo
el almacenamiento ACME de `/data`. Esto **no valida DNS ni HTTPS publico**.

Ambos backends ejecutan `exotic-backend:vm-domains-20261105-be80296d2`:

```text
Image ID: sha256:9f55b40b681102174c93b488e7fb6e4651be21b2503d4c164ea4dacfaee70dd9
JAR SHA256: f3c30ac373c30df1fbadb69883df37eefb168c00f067259387ea93748c34e5bd
```

Spring arranco en 414,193 s en staging y 157,793 s en produccion, con sus
cuotas de CPU diferentes. Las bases no se recrearon ni restauraron en este
paso. El historial Flyway completo sigue igual: 115 filas, baseline 2,
114 SQL exitosas, ultima version 118, cero fallidas. No se modificaron
migraciones, no se ejecuto repair/clean/baseline y Hibernate sigue en validate.

Evidencia privada en `/srv/exotic/private/subdomains-20261105/`:

- `private-smoke-staging.json` y `private-smoke-production.json`.
- `tls-routing-probe.json` y el certificado publico de la CA temporal.
- `final-verification.json`: contenedores, cuotas, puertos, DNS y Compose.
- Copias anteriores de configuracion y dumps de precaucion de cada base,
  con permisos privados. No sustituyen el backup externo de recuperacion.

Para terminar la publicacion se requiere confirmar la reserva de IP con el
administrador GCP, agregar los cuatro registros por el propietario del dominio
y comprobar emision ACME y funcionamiento desde el navegador. La VM esta
preparada para esos registros. Render sigue activo; no se sincronizaron las
escrituras posteriores a la copia inicial ni se realizo un corte de usuarios.
