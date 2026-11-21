# Verificación de BPMN

## Actualización 0.1.3: render simbólico y rombo vacío

El 20 de noviembre de 2026, una captura del usuario reveló un defecto que las
comprobaciones de 0.1.2 no detectaban: GTK renderizaba los iconos simbólicos
como figuras sólidas y perdía sus contornos y marcadores. Decodificar el SVG
con GdkPixbuf y resolver su nombre en el tema no bastaba para verificar cómo
se mostraba en la paleta. La evidencia de 0.1.2 se conserva debajo con ese
alcance limitado.

Se sustituyeron los trazos por contornos cerrados con huecos reales. La prueba
visual utiliza ahora `Gtk.IconPaintable.snapshot_symbolic`, `Gtk.Snapshot` y
`Gsk.CairoRenderer.render_texture`: la misma ruta simbólica que produce el
defecto. Se renderizaron e inspeccionaron los 15 iconos a 16, 24 y 32 píxeles,
con colores de primer plano claros y oscuros aplicados por GTK. Las imágenes
anteriores y corregidas están en las carpetas `original-0.1.2` y `fixed-0.1.3`
de `temp/bpmn-palette-fix-20261120/grace` en el workspace.

La prueba de regresión detecta el relleno de los iconos anteriores, sin depender
del número de herramientas. Su ejecución aislada contra 0.1.2 terminó con los
fallos de aserción esperados; la comprobación negativa terminó con `PASS` en
`temp/bpmn-palette-fix-20261120/negative-original/result.txt`.

La paleta añade **Compuerta exclusiva sin marcador**. Comparte el tipo exclusivo
con la herramienta con X. El indicador `isMarkerVisible` pertenece a cada figura
`BPMNGatewayItem`, con valor predeterminado `True` para conservar el aspecto de
los modelos anteriores. El panel permite cambiar **Mostrar X en esta vista**;
la compuerta paralela conserva siempre su +. No cambian los tipos semánticos
ni las reglas de conexión o validación de flujos.

**105 pruebas aprobadas**: 48 de modelo y operaciones, 36 de diagramas y 21
del editor y servicio. Incluyen render simbólico real, huecos, marcadores,
recoloreado, imágenes distintas, creación del rombo vacío, dibujo, vistas
independientes, copia completa y por vínculo, undo/redo, guardado/reapertura,
lectura de modelos sin la nueva propiedad y checkbox con sensibilidad según
el tipo de compuerta. La integración con los cuatro plugins en dos sesiones
también terminó con `PASS`.

Se repitieron las 105 pruebas y la integración sobre el wheel 0.1.3 instalado
en una carpeta temporal, con el mismo resultado.

Evidencia desde fuentes:
`C:\Users\hardp\AppData\Local\Temp\gaphor-bpmn-tests-af6ca2ea-cb5d-4620-8103-09e94ea74a4b`.

Evidencia del wheel temporal:
`C:\Users\hardp\AppData\Local\Temp\gaphor-bpmn-tests-b4f2ee6c-c913-44f6-ad5b-158ccdc566a7`.

La comprobación corresponde a Windows y Gaphor 3.3.2, sin ventanas visibles
ni modelos del usuario como archivos de prueba. Los atlas muestran el render
simbólico real de GTK, aunque no son capturas del escritorio del usuario.

Se instaló 0.1.3 en `C:\Users\hardp\.local\gaphor\plugins-2`, respaldando
0.1.2 en `temp/bpmn-palette-fix-20261120/backup-0.1.2` del workspace. Los ocho
módulos y los 15 SVG instalados coinciden por SHA-256 con las fuentes, los 50
archivos de los otros plugins conservan sus huellas y existe una única
distribución BPMN, versión 0.1.3.

Un proceso nuevo de Gaphor verificó el descubrimiento nativo, el render
simbólico de los 15 iconos instalados, sus centros transparentes, los botones
y cursores nativos, las tres herramientas de compuerta y el control del marcador
por vista. Resultado: `PASS`, sin inyectar fuentes ni abrir ventanas visibles.
Evidencia: `temp/bpmn-palette-fix-20261120/native-installed-report.txt` del
workspace. Las ventanas abiertas antes de actualizar requieren reinicio.

## Actualización 0.1.2: iconos de la paleta

El 20 de noviembre de 2026 se incorporaron 14 SVG simbólicos propios para las
herramientas BPMN. El lenguaje registra su directorio en `Gtk.IconTheme` al
consultar la paleta, sin duplicar rutas al repetir la consulta en varias
instancias. Los recursos se incluyen explícitamente en el paquete y sus nombres
tienen el prefijo `exotic-bpmn-`.

**100 pruebas aprobadas**: 48 de modelo y operaciones, 32 de diagramas y 20
del editor y servicio. La nueva prueba resuelve cada icono con GTK, comprueba
que procede del paquete, lo decodifica con GdkPixbuf a 16 píxeles y verifica
que las 14 imágenes son visibles y diferentes. También verifica el registro
idempotente al consultar la paleta desde dos instancias del lenguaje.

La integración con los cuatro plugins del repositorio en dos sesiones terminó
con `PASS`. Se repitieron las 100 pruebas y la integración sobre el wheel
0.1.2 instalado en una carpeta temporal, con el mismo resultado.

Evidencia desde la copia temporal de fuentes:
`C:\Users\hardp\AppData\Local\Temp\gaphor-bpmn-tests-670ab474-c322-4308-b410-53b79e42444b`.

Evidencia del wheel instalado temporalmente:
`C:\Users\hardp\AppData\Local\Temp\gaphor-bpmn-tests-1da958a0-ff84-4a8c-990a-c75a324e2a59`.

Se inspeccionaron atlas claros y oscuros a 16, 24 y 32 píxeles. Estos atlas
permiten revisar las geometrías; no son capturas de la aplicación del usuario.
La prueba de GTK acredita la resolución de los recursos también usados por
los iconos de arrastre y el cursor de creación. No se añadieron dependencias
ni se modificaron tipos, reglas o figuras del diagrama.

Esta verificación corresponde a Windows y Gaphor 3.3.2. Se utilizaron modelos
temporales y ventanas de prueba ocultas. `ExoticApp.gaphor` conservó su SHA-256:
`C60F56C01EE2B01143D40B37F36B30BB70F754E7C0476ABA0820A73F3B8497B0`.

Se instaló 0.1.2 en `C:\Users\hardp\.local\gaphor\plugins-2`, conservando una
copia de 0.1.1 en
`C:\Users\hardp\Desktop\exotic_ws\temp\bpmn-palette-icons-20261120\backup-0.1.1`.
Los ocho módulos Python y los 14 SVG instalados coinciden por SHA-256 con las
fuentes. Los 50 archivos de los otros plugins conservan sus huellas y existe
una única distribución BPMN, versión 0.1.2.

Un proceso nuevo de Gaphor comprobó el descubrimiento nativo del lenguaje, la
resolución de los 14 iconos instalados y la construcción de los botones y
cursores nativos. Resultado: `PASS`, sin inyectar fuentes, modificar el cargador,
presentar ventanas, abrir modelos del usuario ni escribir sus preferencias.
Evidencia:
`C:\Users\hardp\Desktop\exotic_ws\temp\bpmn-palette-icons-20261120\native-installed-report.txt`.
Las ventanas de Gaphor que ya estaban abiertas necesitan reiniciarse para
cargar esta actualización; no se cerraron durante la comprobación.

## Actualización 0.1.1: organización en paquetes

El 4 de noviembre de 2026 se añadió organización de colaboraciones dentro de
paquetes UML y referencia explícita desde el diagrama a la colaboración. Esta
separación permite que el diagrama y un paquete `childs` sean hermanos sin
alterar la propiedad semántica de procesos, carriles, nodos y flujos. Se conserva
la lectura de los modelos anteriores, sin estas referencias opcionales.

**99 pruebas aprobadas**: 48 de modelo y operaciones, 31 de diagramas y 20 del
editor y servicio. La integración con los otros cuatro plugins en dos sesiones
reales también terminó con `PASS`. Incluye árbol, creación desde paquetes,
herramientas sin duplicar colaboraciones, serialización, undo/redo y protección
del borrado de una carpeta referida por un diagrama externo.

Resultados de fuentes:
`C:\Users\hardp\AppData\Local\Temp\gaphor-bpmn-tests-bf700c5c-f03d-427d-9faa-c1651208f510`.

Se instaló la versión 0.1.1 en
`C:\Users\hardp\.local\gaphor\plugins-2`. Los ocho módulos instalados coinciden
por SHA-256 con las fuentes comprobadas; los 50 archivos de los otros plugins
conservan sus hashes. Existe una única distribución BPMN, versión 0.1.1.
Los procesos de Gaphor que estaban abiertos requieren reinicio para cargarla.

Se comprobó también el descubrimiento nativo de la instalación 0.1.1, sin
inyectar fuentes ni reemplazar el cargador de plugins. Dos sesiones nuevas
abrieron la copia inicial detallada de Exotic con el proceso de ingreso de
producto terminado: árbol, pertenencia a paquetes, 18 nodos, 22 secuencias, conexiones,
validación final y guardado/reapertura temporal terminaron con `PASS`.

La preparación aditiva preservó los 321 IDs originales: 320 registros quedaron
idénticos byte por byte y el registro de `Applicacion` sólo recibió las dos
referencias necesarias al nuevo módulo. Los tres diagramas originales y la
hoja de estilo se conservaron literalmente; aquella copia añadió 101 registros sin
referencias pendientes. Esta comprobación corresponde a la copia preparada;
por sí sola no acredita su aplicación al archivo principal.

Evidencia de la copia preparada y la instalación nativa:
`C:\Users\hardp\AppData\Local\Temp\exotic-ingreso-bpmn-e1ffb7f8-fe54-4834-8d16-2b94e6747a3f\installed-report.txt`.

### Copia simplificada del ingreso de producto terminado

A petición del usuario, se simplificó la copia preparada: seis tareas, una
compuerta de validación, inicio y fin (**9 nodos y 9 secuencias**), dos carriles
y una nota de alcance. El registro del ingreso se representa como tarea, sin
marcador de subproceso. La jerarquía de paquetes se conserva.

La vista declara que representa el recorrido principal. La documentación de
sus actividades conserva ausencia de pendientes, validaciones y permisos,
HyL local y su invalidación al modificar datos, errores y reintentos, conflictos
que requieren recargar y revisar, atomicidad e idempotencia, Calidad no
bloqueante, lote existente y efectos contables/documentales pendientes. El fin
sólo corresponde a un cierre aceptado o un resultado idempotente existente.

Chani revisó la fidelidad con el AS-IS y Thufir verificó representación y
pertenencia de las figuras. La copia completa pasó nuevamente apertura,
conexiones, árbol, validación final y guardado/reapertura en dos sesiones de
Gaphor con el plugin instalado. La preparación conserva los 321 IDs originales,
320 registros literales y sólo añade referencias en el paquete `Applicacion`;
añade 51 registros nuevos sin referencias pendientes.

Se actualizó únicamente la copia temporal `ExoticApp-con-BPMN.gaphor`; la
anterior quedó como `ExoticApp-con-BPMN-detallado.gaphor` en la misma carpeta.
`ExoticApp.gaphor` principal sigue intacto, pendiente de confirmar el estado
guardado del modelo abierto antes de incorporar la adición.

Evidencia:
`C:\Users\hardp\AppData\Local\Temp\exotic-ingreso-bpmn-e1ffb7f8-fe54-4834-8d16-2b94e6747a3f\simplified-installed-report.txt`.

Las secciones siguientes conservan el historial de la entrega 0.1.0. Sus
referencias a la huella intacta de `ExoticApp.gaphor` corresponden a aquella
entrega del plugin, anterior a la solicitud de añadir el primer proceso BPMN.

## Historial: entrega 0.1.0

Fecha: **4 de noviembre de 2026**. Entorno: Windows, Gaphor **3.3.2** y su
runtime Python **3.14.4**. El empaquetado utilizó Python **3.12.14**, pip,
setuptools y wheel disponibles localmente, sin descargar dependencias.

**Estado actual: instalado en el perfil de Windows `hardp`.** La comprobación
de la instalación permanente se documenta al final; los resultados anteriores
de instalaciones temporales se conservan como evidencia de desarrollo.

## Resultado

**82 pruebas aprobadas**: 41 del modelo y las operaciones, 23 de diagramas y
18 del editor y servicio. La integración en dos sesiones reales de Gaphor
también terminó con estado `PASS`.

Se repitieron ambas comprobaciones sobre el wheel construido e instalado en
una carpeta temporal: **82 aprobadas e integración aprobada**. El runner
comprobó que se importaba ese paquete, su versión y sus tres entry points.

La instalación temporal no activó BPMN en el perfil de Gaphor del usuario.

## Comprobaciones realizadas

- Namespace, tipos, relaciones, composición y pertenencia al proceso.
- Asignación de carriles independiente del ámbito; protección ante traslado
  accidental a otro participante.
- Combinaciones de eventos y dirección de secuencias y mensajes; varios mensajes
  entrantes a inicio y límite de uno para intermedios de mensaje.
- Límites de subprocesos, compuertas exclusiva/paralela, condiciones y flujo
  predeterminado; diagnóstico de borrador frente a validación final.
- Conexiones reales de Gaphor, puertos de eventos y rombos, reconexión,
  restauración de conexiones incompletas y protección de varias representaciones.
- Serialización y reapertura de propiedades, booleanos, referencias y figuras.
- Copia por vínculo, copia completa de pools y rechazo transaccional de copias
  que perderían dependencias.
- Cancelación, guardado, detección de borradores antiguos, rollback y undo/redo.
- Protección del borrado nativo y eliminación explícita de un participante con
  su proceso, contenido y flujos; undo reconstruye objetos con sus mismos IDs.
- Coexistencia con Propiedades 0.3.0, importador de carpetas 0.1.1,
  Copiar referencias 0.1.0 y PostgreSQL 0.1.0, cargados desde las fuentes locales.
- Propiedades existentes y documentación BPMN independientes, menú compartido
  sin duplicación, dos sesiones y cierre independiente de sus servicios.
- Exportación nativa a PNG y SVG de un catálogo de símbolos y de una colaboración
  con decisión, retrabajo, carriles, subproceso, mensajes y anotación.

Se inspeccionaron visualmente las exportaciones. Se corrigieron mínimos de
tamaño del pool cerrado, contaminación de paths Cairo entre figuras y puertos
rectangulares que no correspondían al contorno de eventos o compuertas. Los
cruces de líneas del ejemplo dependen de su disposición manual; no se incluye
un algoritmo de enrutamiento automático.

## Evidencia local

Pruebas finales desde fuentes:

```text
C:\Users\hardp\AppData\Local\Temp\gaphor-bpmn-tests-92767026-8d6f-4e09-9b93-6bfa38be4e39
```

Pruebas sobre el paquete instalado temporalmente:

```text
C:\Users\hardp\AppData\Local\Temp\gaphor-bpmn-tests-7dad29ff-d21e-4c3a-8bc5-e5a555f8544e
```

Cada carpeta conserva `results.txt`, `status.txt`, `integration.txt`,
`integration-status.txt` y exportaciones temporales. Las rutas temporales
pueden desaparecer al limpiar Windows; los tests del repositorio permiten
regenerarlas. Los mensajes de rollback de los casos negativos son esperados.

Wheel construido:

```text
C:\Users\hardp\AppData\Local\Temp\gaphor-bpmn-package-14412ef6-2a3f-4c3a-9803-ba4d38d9ecd6\wheels\gaphor_bpmn_model-0.1.0-py3-none-any.whl
SHA256: 52fe079bd063bbec6c09801ea56abcc46e9d4e56683c32ce56d1ae802851b79f
```

También se comprobó la sintaxis Python, PowerShell y Bash. Los scripts de
instalación permanente se entregan para su ejecución posterior; no se ejecutaron
contra el perfil del usuario ni se modificó la instalación de Gaphor.

## Conservación del modelo y límites

`ExoticApp.gaphor` conserva la misma huella antes y después del trabajo:

```text
CF9E9C65F6DF5FEC6F9A6FDA07107378922535D6A268BBC6DFB4D2592D4A64BE
```

No se modificaron los cuatro plugins anteriores ni los diagramas del usuario.
Las pruebas se realizaron en proyectos temporales; la persistencia de preferencias
del servicio nativo de Gaphor se sustituyó por un stub dentro del proceso de
integración para evitar escribir en su caché. No se reemplazó la persistencia
de los modelos que se estaba verificando.

Pendientes o fuera del alcance:

- Ejecución en Linux y Flatpak, y otras versiones de Gaphor.
- Interacción manual completa en la aplicación del usuario después de instalar;
  la integración construye widgets y sesiones reales, pero suprime `present()`
  para no abrir ventanas de prueba en el escritorio.
- Certificación de conformidad BPMN, ejecución, simulación e intercambio BPMN XML.
- Prueba general de ausencia de bloqueos, terminación o corrección de condiciones.

El subconjunto entregado está descrito en `README.md`. El análisis de los plugins
existentes y la relación con Gaphor se conservan en `ANALISIS_PLUGINS.md`.

## Instalación permanente en este PC

El 4 de noviembre de 2026 el usuario autorizó instalar el plugin. Se ejecutó
`install.ps1` como `hardp`, con Python 3.12.14 y destino explícito:

```text
C:\Users\hardp\.local\gaphor\plugins-2\gaphor_bpmn_model
C:\Users\hardp\.local\gaphor\plugins-2\gaphor_bpmn_model-0.1.0.dist-info
```

La instalación terminó correctamente y sin descargar dependencias. Piter
comprobó que los ocho módulos instalados coinciden por SHA-256 con las fuentes,
que existe una única distribución BPMN 0.1.0 y que los 50 archivos previos de los
otros plugins y sus metadatos conservan sus hashes originales.

Se ejecutó un proceso nuevo de `C:\Program Files\Gaphor\gaphor.exe`, bajo la
cuenta real `hardp`, con script y resultados en una carpeta temporal. Esta
comprobación usó el descubrimiento nativo: no insertó las fuentes en `sys.path`,
no añadió lenguajes o servicios a mano y no sustituyó `load_entry_points`.

Resultado: **PASS**. Confirmó distribución y tres entry points únicos,
importación de los ocho módulos desde el perfil instalado, lenguaje BPMN,
herramientas, menú y servicio compatibles en dos sesiones. También comprobó
la coexistencia con los cuatro plugins anteriores y el cierre independiente
de sesiones. Sólo se suprimieron ventanas de prueba y guardado de preferencias;
no se abrieron modelos del usuario.

Evidencia de la comprobación instalada:

```text
C:\Users\hardp\AppData\Local\Temp\gaphor-bpmn-installed-check-87911add-3d4e-4fdb-8f51-3d2d307378e1\report.txt
```

Gaphor estaba abierto antes de instalar. Sus procesos existentes no se cerraron
ni se reiniciaron; el usuario debe guardar su trabajo y reiniciar la aplicación
para cargar BPMN en esas ventanas. La prueba acredita la carga en procesos
nuevos, no la actualización de los que ya estaban abiertos.
