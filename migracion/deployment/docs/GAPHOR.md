# Despliegue: origen Render y propuesta de migración en Gaphor

Revisión de la versión local guardada de `ExoticApp.gaphor`: **4 de noviembre
de 2026**. Por solicitud explícita del usuario se añadió el diagrama
`deployment migracion`, conservando los diagramas anteriores. Este documento
registra el diseño y su correspondencia con la configuracion. El estado real de
las copias privadas se registra en DESPLIEGUE_INICIAL.md; no se ha hecho el corte
de usuarios ni DNS desde Render.

## Alcance modelado comprobado

Se leyeron el diagrama `Despliegue`, la pertenencia de sus elementos, sus
relaciones y notas. Identificadores relevantes:

| Elemento actual | Identificador en el modelo | Responsabilidad o relación comprobada |
| --- | --- | --- |
| Diagrama `Despliegue` | `5230413a-c535-11f1-8d22-b81ea434d48d` | Vista del despliegue existente. |
| Nodo `render.com` | `583f61aa-c535-11f1-8d22-b81ea434d48d` | Contiene backend y PostgreSQL; su nota expresa dos entornos: production y staging, con web service, static site y PostgreSQL. |
| Dispositivo `PC - usuario` | `354c6aca-c536-11f1-8d22-b81ea434d48d` | Contiene la representación de `FrontEnd`. |
| Nodo `FrontEnd` | `8cfcf474-c536-11f1-8d22-b81ea434d48d` | Representa el frontend ejecutado por el usuario; la publicación estática se menciona en la nota de Render. |
| Nodo `Backend - Spring` | `97957bea-c536-11f1-8d22-b81ea434d48d` | Su nota especifica Docker en Render y almacenamiento persistente. |
| Nodo `PostgresDatabase` | `1efbd8c2-c537-11f1-8d22-b81ea434d48d` | Persistencia relacional del backend dentro de Render. |
| Asociación `HTTP` | `fac07e18-c536-11f1-8d22-b81ea434d48d` | Conecta frontend y backend. |
| Asociación `SQLPostgreSQL - JDBC` | `ea5f3352-c5c2-11f1-aea3-b81ea434d48d` | Conecta backend y PostgreSQL. |

La representación del frontend dentro del PC y su entrega por un sitio estático
son responsabilidades distintas; no interpretar el nodo de ejecución del
navegador como un contenedor actual de Render. La duplicación por entorno está
expresada en una nota, sin exigir duplicar todo el dibujo para comprenderla.

El hash SHA-256 anterior a añadir la vista de migración fue:

```text
CF9E9C65F6DF5FEC6F9A6FDA07107378922535D6A268BBC6DFB4D2592D4A64BE
```

El archivo permanece bajo mantenimiento manual del usuario; esta edición fue
autorizada expresamente. Si cambia después de esta revisión, consultar la
nueva versión antes de declarar congruencia.

## Propuesta de destino representada

Ubicación en el árbol: `Exotic-App / Despliegue / Migración VM /
deployment migracion`. Identificador del diagrama:
`176e4884-d894-11f1-8eb8-bc09b9551b3f`. La vista está marcada como **PROPUESTA**;
el diagrama original `Despliegue` conserva el origen Render.

La propuesta tiene una VM de Google Compute Engine con Debian 13 y **dos
proyectos Compose**, uno de producción y otro de staging. Cada proyecto define
`database`, `backend` y `web`; un tercer proyecto administra un único proxy
común. El resultado propuesto es **siete contenedores: 3 + 3 + 1**. Ese número
corresponde a esta composición concreta, no a una exigencia de React, Spring,
PostgreSQL o Docker.

Cada entorno mantiene su PostgreSQL 18, backend y publicación estática, con
datos y credenciales separados. `web` entrega el `dist` precompilado mediante
Caddy en `8080`; el proxy común termina HTTPS y enruta por nombre de dominio.
Un dominio web y un dominio API por entorno conservan todas las rutas del
backend, incluidas las que ya comienzan por `/api`.

Los volúmenes externos previstos son
`exotic-ENVIRONMENT-postgres`, `exotic-ENVIRONMENT-uploads` y
`exotic-ENVIRONMENT-logs`, sustituyendo `ENVIRONMENT` por `production` o
`staging`. Los certificados y estado del proxy común usan
`exotic-edge-caddy-data` y `exotic-edge-caddy-config`. Los archivos de secretos
del host no son volúmenes de código ni se incorporan a las imágenes.

Las redes externas `exotic-production-edge` y `exotic-staging-edge` permiten
enlazar el proxy con cada entorno. La comunicación backend–database usa una
red separada de cada proyecto; las bases no publican un puerto hacia Internet.
Las redes no dan disponibilidad independiente: ambas aplicaciones, bases,
documentos y proxy siguen compartiendo la misma VM y su disco. La vista
representa ese límite común de recursos y fallo.

Construcción y pruebas se ubican fuera de la VM: CI o un proceso externo
controlado producen la imagen del backend y el `dist`; la VM obtiene los
artefactos publicados. Una futura CI no está implementada por estos archivos
y el pipeline actual del backend no constituye su validación. Las pruebas
automatizadas no son un octavo servicio permanente añadido a esta propuesta.

## Presupuesto de recursos próximo al 70 %

La referencia es el inventario del 4 de noviembre de 2026 en
[CAPACIDADES_VM.md](../../../../ssh_gcloud/CAPACIDADES_VM.md): **2 vCPU**,
**9,716 GiB de RAM reconocida por Linux** y disco persistente de **50 GiB**.
Los 10 GiB nominales no se utilizan como denominador de la memoria disponible
para presupuestar procesos.

| Entorno | Contenedor | Límite CPU propuesto | Límite RAM propuesto |
| --- | --- | ---: | ---: |
| Producción | `web` | 0,04 vCPU | 128 MiB |
| Producción | `backend` | 0,65 vCPU | 2560 MiB |
| Producción | `database` | 0,30 vCPU | 1536 MiB |
| Pruebas / staging | `web` | 0,03 vCPU | 128 MiB |
| Pruebas / staging | `backend` | 0,20 vCPU | 1536 MiB |
| Pruebas / staging | `database` | 0,10 vCPU | 768 MiB |
| Compartido | `edge` | 0,08 vCPU | 256 MiB |
| **Total** | **7 contenedores** | **1,40 vCPU** | **6912 MiB = 6,75 GiB** |

Esto equivale a **70 % de CPU** y **69,5 % de la RAM reconocida**. El margen
presupuestario es **0,60 vCPU y 2,966 GiB**, para Debian, Docker y operaciones
de mantenimiento. Son techos propuestos, no consumo obligatorio, previsiones
de uso ni reservas garantizadas de CPU. No se debe aumentar el consumo para
alcanzar un porcentaje. Los procesos adicionales del host también consumen
recursos y deben vigilarse. La distinción entre cuotas, límites de memoria y
prioridad está documentada en
[restricciones de recursos de Docker](https://docs.docker.com/engine/containers/resource_constraints/).

La prioridad presupuestaria corresponde a producción. El límite de CPU del
backend de staging es deliberadamente menor; validar tiempos de arranque,
salud, latencia y concurrencia antes de adoptarlo. Las pruebas automatizadas,
compilaciones y generadores de carga quedan fuera de esta VM. La capacidad
bajo carga y el comportamiento simultáneo de ambos entornos siguen pendientes
de verificación.

Para el disco se propone **ocupación de la raíz no superior al 70 %**: unos
34 GiB usados y 15 GiB de margen sobre los 48,978 GiB de filesystem medidos.
Es un objetivo operativo con alertas, rotación y limpieza, no una cuota por
volumen ni una partición creada. Datos, documentos, WAL, registros, imágenes y
artefactos comparten ese espacio. Los backups externos tienen capacidad y
retención propias, todavía por configurar.

**Configuración sincronizada con este presupuesto para el piloto inicial:**
`compose.yaml`, `compose.edge.yaml` y los ejemplos de `env/` ya declaran los
límites de esta tabla. Reemplazan los 5,5 GiB y 2,95 vCPU anteriores. El heap
de Java conserva un máximo del 60 % del límite del contenedor; PostgreSQL
mantiene sus buffers explícitos. Validar su comportamiento con carga real.
La nota del diagrama que decía que los límites seguían pendientes conserva
su carácter histórico y debe actualizarse manualmente al registrar el piloto;
el modelo no se modifica como consecuencia de la solicitud de despliegue.

## Criterio de simplificación de la vista

La vista muestra VM, navegador, siete contenedores, agrupaciones de entorno,
conexiones web/API/JDBC, persistencia por entorno, disco compartido y las
responsabilidades externas de construcción/pruebas y respaldo. Las
agrupaciones, CI y almacenamiento no cuentan como contenedores adicionales.
Los volúmenes aparecen en notas y las rutas operativas en las notas de los
elementos; se evitan figuras para cada archivo, variable o secreto.

Las comunicaciones son relaciones UML editables y conectadas a sus nodos.
Los nombres web/API distinguen los dominios de cada entorno; el proxy conserva
las URI del backend. Los detalles de redes, credenciales, imágenes y límites
se conservan en las notas de los elementos y los documentos asociados.

El inventario siguiente localiza los archivos por responsabilidad sin exigir
dibujar cada uno como artefacto. Los ejemplos no son instancias operativas,
secretos ni evidencia de despliegue.

Los cambios de seleccion de API y CORS aplicados el 5 de noviembre y sus
verificaciones pendientes se detallan en [COMPATIBILIDAD.md](COMPATIBILIDAD.md).
La preparacion de infraestructura y la comprobacion funcional son evidencias
distintas; no se declara un corte desde Render por configurar los dominios.

## Inventario de archivos de preparación por responsabilidad

Todas las rutas siguientes son relativas a `exotic-app-architecture/` y
corresponden al inventario de esta entrega; el usuario puede representarlas
como artefactos cuando ayuden a preservar la intención.

| Archivo | Responsabilidad que debe poder localizarse |
| --- | --- |
| `migracion/deployment/README.md` | Alcance, orden de preparación y enlaces a los procedimientos. |
| `migracion/deployment/compose.yaml` | Servicios database/backend/web, configuración, persistencia y redes de un entorno. |
| `migracion/deployment/compose.edge.yaml` | Proxy común, puertos públicos, redes y almacenamiento de certificados. |
| `migracion/deployment/compose.edge.private.yaml` | Variante temporal por SSH, mismo proxy y presupuesto, cuatro listeners loopback. |
| `migracion/deployment/compose.pilot.yaml` | Override privado para ambos entornos; sin puertos de aplicaciones. |
| `migracion/deployment/config/edge.private.Caddyfile` | Routing privado a web/API de cada entorno, conservando URI. |
| `migracion/deployment/config/edge.loopback.Caddyfile` | Listeners SSH y limpieza de cabeceras compartidos por ambas variantes de edge. |
| `migracion/deployment/env/edge.private.env.example` | Imagen fijada y limites del acceso por SSH. |
| `migracion/deployment/env/production.env.example` | Parámetros no secretos de producción y bloqueo de compatibilidad sin confirmar. |
| `migracion/deployment/env/staging.env.example` | Parámetros no secretos de staging y bloqueo de compatibilidad sin confirmar. |
| `migracion/deployment/env/edge.env.example` | Parámetros no secretos del proxy y sus cuatro nombres de dominio. |
| `migracion/deployment/config/edge.Caddyfile` | Entrada y configuración común del proxy. |
| `migracion/deployment/config/frontend.Caddyfile` | Publicación estática del `dist` y fallback de la SPA. |
| `migracion/deployment/config/sites/production.caddy.example` | Ejemplo de routing web/API de producción, conservando rutas del backend. |
| `migracion/deployment/config/sites/staging.caddy.example` | Ejemplo de routing web/API de staging, conservando rutas del backend. |
| `migracion/deployment/postgres/init-app-user.sh` | Inicialización controlada del rol/base de aplicación; no sustituye una restauración ni modifica por sí solo un cluster existente. |
| `migracion/deployment/postgres/entrypoint.sh` | Copia privada en tmpfs del secreto que debe leer el usuario PostgreSQL durante la inicialización. |
| `migracion/deployment/scripts/common.sh` | Funciones compartidas de validación y selección de entorno/contexto. |
| `migracion/deployment/scripts/stack.sh` | Validación y operaciones explícitas sobre el stack de aplicación del entorno. |
| `migracion/deployment/scripts/prepare.sh` | Preparación controlada de volúmenes y red del entorno, previa a un despliegue autorizado. |
| `migracion/deployment/scripts/pilot.sh` | Arranque privado tras validar procedencia, esquema/documentos e identidad de imagen. |
| `migracion/deployment/scripts/import-production-copy.sh` | Importacion completa y transaccional a base vacia con backend detenido; documentos propios del destino. |
| `migracion/deployment/scripts/backup.sh` | Obtención controlada de respaldos; no constituye por sí misma una prueba de recuperación. |
| `migracion/deployment/docs/COMPATIBILIDAD.md` | Bloqueos y verificaciones de aplicación antes de habilitar la publicación. |
| `migracion/deployment/docs/SUBDOMINIOS.md` | Cuatro nombres acordados, preparacion aplicada, evidencia y entrega DNS. |
| `migracion/deployment/docs/GAPHOR.md` | Correspondencia entre origen y destino modelados; presupuesto del 70 % y límites pendientes de aplicar a la configuración. |
| `migracion/deployment/docs/RECUPERACION.md` | Restauración, recuperación y criterios de reversión. |
| `migracion/deployment/.gitignore` | Exclusión de parámetros locales, secretos y artefactos que no deben versionarse. |
| `migracion/deployment/.gitattributes` | Convenciones de texto y finales de línea, incluidos scripts Linux. |

Los `.env`, secretos y configuraciones operativas que prepare posteriormente
el operador no forman parte de este inventario versionado. No representar los
valores secretos ni copiar archivos privados del backend al modelo. La clave
SSH y la autenticación local por Pageant siguen documentadas en `ssh_gcloud/`;
no son componentes del backend ni del proceso de construcción de imágenes.

## Límite Windows, WSL y servidor

PowerShell sirve para revisar y copiar los archivos, y para validar la
configuración declarativa con Compose si esa herramienta está disponible.
Los scripts Bash deben comprobarse o ejecutarse en Linux conforme a su alcance.
Debian de WSL puede servir para análisis sintáctico; el Docker Desktop local no
representa el motor de la VM. Las operaciones que crean recursos o publican
servicios requieren el servidor y la autorización correspondientes. Estos
límites pertenecen al procedimiento operativo; no implican desplegar WSL o
Windows dentro de la VM.

## Estado de entrega

**Vista de destino añadida y validada en Gaphor 3.3.2.** Se comprobó carga,
guardado y recarga nativos del modelo con 391 elementos, siete contenedores y
nueve relaciones conectadas. Se revisó visualmente la exportación y se
verificó que los tres diagramas anteriores se renderizan idénticamente. Los
319 elementos previos ajenos al paquete organizador y la hoja de estilo se
conservaron byte a byte; en esos dos elementos solo se añadieron referencias
al paquete nuevo y CSS acotado a `deployment migracion`.

**Limites aplicados y dos copias privadas ejecutandose; carga pendiente.**
Se conservan los bloqueos de publicación por dominio y el diagrama de Render.
El despliegue privado y su verificacion se registran en
[DESPLIEGUE_INICIAL.md](DESPLIEGUE_INICIAL.md). Su acceso por túnel SSH es un
paso temporal de validación, sin afirmar una migración pública realizada.
Queda pendiente de sincronización manual con Gaphor esa modalidad y la nota
histórica de límites. No se declara congruencia global ni disponibilidad productiva.

Actualizacion manual concreta pendiente en `deployment migracion`: registrar
que los siete contenedores y limites ya se aplicaron, describir el acceso
temporal por SSH al edge loopback, la restauracion del mismo origen productivo
en ambos destinos y el UID 1000 de los backends. Conservar como pendientes
dominios/TLS, backup remoto y corte desde Render. El modelo guardado no se
modifico durante esta implementacion.

## Actualizacion del 5 de noviembre: subdominios preparados

Se consulto de nuevo la vista guardada, sus relaciones, jerarquia y notas.
El archivo conserva SHA256
`F63634BE8B1D038E8229FB3B219F37552CEE554D33AF4BBCBB541384DC72A276`;
no se modifico en esta actualizacion. Se mantienen siete contenedores,
volumenes, redes y presupuesto. **Pendiente de sincronizacion manual con
Gaphor**, mediante estas modificaciones concretas a `deployment migracion`:

1. Nombrar las conexiones web/API de produccion como `mrp.prod.exotic.com.co`
   y `mrp.api.prod.exotic.com.co`; las de staging como
   `mrp.staging.exotic.com.co` y `mrp.api.staging.exotic.com.co`.
2. Actualizar la nota del edge: TCP80/443 configurados junto con los cuatro
   listeners loopback para SSH; DNS y certificados ACME publicos pendientes.
   Reserva de la IP 34.30.31.30 pendiente de confirmacion en GCP.
3. En la nota de cada web, indicar dos artefactos de la misma fuente: SSH en
   `/srv` y publico en `/srv-public`, seleccion fija por hostname. El build
   publico recibe `VITE_API_BASE_URL` y `VITE_APP_ENV`; no es otro contenedor.
4. En la nota de cada backend, indicar CORS configurable por lista exacta
   `app.cors.allowed-origins`, con su propia web y los dos origenes localhost
   conservados. Los contratos URI existentes se mantienen completos.
5. Conservar la inicializacion desde una misma copia productiva, aislamiento
   de datos/credenciales, limites ya aplicados y UID 1000. Mantener pendientes
   backup remoto, carga y corte definitivo de usuarios/datos desde Render.

Si se representan artefactos de codigo, las rutas concretas modificadas son
`exotic-app-frontend/src/api/EndPointsURL.tsx`,
`exotic-app-frontend/src/vite-env.d.ts` y
`exotic-app-backend/src/main/java/exotic/app/planta/config/CorsConfig.java`.
Las nuevas plantillas publicas son `exotic-app-frontend/.env.staging.example`
y `exotic-app-frontend/.env.production.example`. No modelar valores secretos.
