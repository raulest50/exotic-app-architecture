# Diagramas de procesos BPMN 0.1.1

Plugin independiente para **Gaphor 3.3.2**, orientado al modelado descriptivo de
procesos mediante un subconjunto de BPMN 2.0.2. Añade el lenguaje **BPMN**, sus
herramientas, figuras, relaciones persistentes y propiedades.

No es un motor de procesos y no afirma conformidad completa con BPMN. Esta
versión guarda archivos `.gaphor`; no importa ni exporta XML `.bpmn`.

La versión 0.1.1 permite organizar una colaboración BPMN dentro de un paquete
UML. El diagrama puede pertenecer al paquete del proceso y los elementos a su
subpaquete `childs`: una referencia explícita conserva la relación entre ambos.
Los modelos anteriores con el diagrama dentro de la colaboración siguen
soportados. Reinicia Gaphor para cargar esta versión antes de abrir modelos que
utilicen esta organización.

**Los archivos que contengan elementos BPMN requieren este plugin para abrirse.**
Conserva el paquete y su versión junto al proyecto. Desinstalarlo no convierte
los elementos en UML. El desarrollo y las pruebas no modifican `ExoticApp.gaphor`.

## Instalación en Windows

Se necesita un Python >= 3.12 con pip, setuptools >= 68 y wheel para empaquetar.
La ejecución del plugin utiliza el Python que ya incluye Gaphor; no se crea un
entorno por plugin ni se instalan dependencias adicionales.

Desde esta carpeta:

```powershell
.\install.ps1 -PythonExe 'C:\ruta\a\python.exe'
```

El instalador comprueba Gaphor 3.3.2 y utiliza por defecto
`%USERPROFILE%\.local\gaphor\plugins-2`. No descarga dependencias ni sustituye
los otros plugins. Reinicia Gaphor después de instalar y selecciona **BPMN** en
el selector de lenguaje. La creación del código fuente no instala por sí sola
el plugin en ese perfil.

## Empezar un diagrama

1. Selecciona **BPMN** y crea **New Diagram → Diagrama BPMN** desde el árbol.
   También puedes usar **Tools → Custom tools → BPMN → Nuevo diagrama BPMN**.
2. Usa el pool abierto inicial si el diagrama ya incluye uno. Si no, dibuja un
   **Pool abierto** para el participante cuyo proceso vas a representar.
   Un pool tiene un proceso propio. Un **Pool cerrado** representa un participante
   externo cuyo trabajo interno no se detalla.
3. Añade **Carril** dentro de un pool abierto, y tareas, eventos o compuertas
   dentro del pool o de sus carriles. Con varios pools abiertos, dibuja dentro
   del contenedor correspondiente para evitar asignaciones ambiguas.
4. Para las líneas, arrastra desde el **origen hacia el destino**. La secuencia
   representa el orden dentro del proceso; el mensaje comunica participantes
   diferentes. La asociación enlaza una anotación con el elemento que explica.
5. Selecciona un elemento y pulsa **Editar propiedades BPMN…** en el panel lateral
   o en el menú BPMN. Elige el tipo de evento, compuerta o secuencia cuando proceda.
   **Guardar** aplica una transacción al modelo; **Ctrl+S** guarda el archivo.
6. Usa **Validar BPMN** para revisar el subconjunto implementado. El informe
   distingue errores de avisos y permite volver al diagrama para corregirlos.

F2 conserva la edición nativa del nombre. El doble clic del plugin Propiedades
sigue disponible. El campo **Documentación BPMN** es propio del nuevo lenguaje;
la Descripción y Nota del editor existente conservan sus campos independientes.

## Elementos y propiedades

| Elemento | Alcance |
| --- | --- |
| Evento de inicio | Ninguno, mensaje de recepción y temporizador |
| Evento intermedio | Ninguno de lanzamiento, mensaje de recepción o envío, temporizador de recepción |
| Evento de fin | Ninguno y mensaje de envío |
| Tarea | Tarea genérica con nombre y documentación |
| Subproceso | Integrado, colapsado, con marcador «+»; no se ofrece editor de descomposición interna |
| Compuerta | Exclusiva XOR y paralela AND |
| Pool | Participante expandido con proceso; participante cerrado sin trabajo interno visible |
| Carril | Un nivel dentro del proceso; asignación adicional de los nodos |
| Secuencia | Ordinaria, condicional con expresión descriptiva y predeterminada |
| Mensaje | Entre participantes distintos, con extremos compatibles |
| Anotación y asociación | Texto explicativo y conector sin dirección hacia un elemento soportado |

Las condiciones se guardan como texto; no se ejecutan ni se comprueba su
exhaustividad. Las repeticiones pueden representarse mediante retornos de
secuencia. No se incluyen marcadores de bucle o multiinstancia de actividades.

## Pertenencia, referencias y edición

La colaboración contiene participantes y procesos. Un nodo pertenece a un
proceso o al ámbito interno de un subproceso; su carril es una referencia
adicional. Moverlo entre carriles del mismo proceso conserva su ámbito. No se
traslada silenciosamente a otro proceso al arrastrarlo sobre otro pool.

Se conservan referencias a objetos al renombrar. Las conexiones de secuencia
entre procesos o atravesando un subproceso se rechazan. También se rechazan
mensajes dentro del mismo participante y extremos incompatibles. Para abrir un
pool cerrado se crea un proceso vacío; para cerrar uno expandido hay que retirar
primero su contenido interno.

El editor usa borradores: cancelar no modifica el modelo; un error de guardado
revierte la transacción. Si el elemento cambió mientras se editaba, hay que cerrar
y volver a abrir el editor antes de guardar el borrador antiguo.

Los diagramas pueden estar incompletos durante el dibujo. La acción explícita
**Validar BPMN** aplica además comprobaciones finales de cardinalidades de eventos,
compuertas y secuencias, sin bloquear el proceso de construcción.

### Borrado y recuperación

El borrado nativo se bloquea cuando perdería extremos de flujos o dejaría un
proceso sin participante. Para borrar un nodo o una anotación, elimina primero
los flujos que lo referencian. Para borrar un participante con su proceso, usa
**Tools → Custom tools → BPMN → Eliminar participante BPMN…** y confirma: se
retiran el pool, su proceso, su contenido y los flujos incidentes dentro de una
sola transacción. **Deshacer** recupera el conjunto y sus referencias.

Eliminar un carril sin asociaciones limpia la asignación de sus nodos y conserva
el proceso al que pertenecen. Una colaboración completa puede eliminarse mediante
el borrado nativo porque incluye sus participantes, procesos y flujos.

## Guardado, copia y varias vistas

Los tipos, propiedades, referencias y figuras se guardan mediante la persistencia
nativa de Gaphor. Arrastrar un elemento del árbol crea otra representación del
mismo objeto; copiar y pegar como vínculo conserva esa identidad.

La copia completa crea objetos nuevos y remapea sus referencias. Entre proyectos
deben incluirse las dependencias: copiar un pool completo incluye su proceso.
Una copia incompleta que perdería extremos o pertenencia se rechaza y revierte.
Cuando una relación aparece en varias vistas, sus extremos se conservan para
evitar que una reconexión cambie solo una representación; los nombres y demás
propiedades siguen siendo editables.

## Pruebas y resultados

En Windows con la instalación habitual de Gaphor:

```powershell
.\test.ps1
```

Las pruebas usan el runtime real de Gaphor y modelos temporales. No utilizan el
archivo `ExoticApp.gaphor` como salida. El script muestra la carpeta de resultados,
archivos `.gaphor` de ejemplo y exportaciones PNG/SVG. La integración de este
repositorio comprueba la coexistencia cargando las fuentes de los cuatro plugins
actuales del repositorio, sin instalar el nuevo plugin en el perfil del usuario.

Los mensajes de rollback corresponden a casos negativos esperados: el resultado
se determina por las aserciones y los archivos `status.txt` e
`integration-status.txt`. `GAPHOR_PLUGIN_PATH` extiende la búsqueda y no garantiza
por sí solo aislamiento del perfil del usuario.

Consulta [VERIFICATION.md](VERIFICATION.md) para el resultado efectivo y las
limitaciones de lo verificado; [ANALISIS_PLUGINS.md](ANALISIS_PLUGINS.md) conserva
el análisis de los plugins anteriores y las decisiones de integración.

## Linux

Preparado para una instalación nativa de Gaphor 3.3.2 con GTK y Python adecuados;
**pendiente de ejecución en Linux y sin verificación de Flatpak**.

```bash
bash install.sh --python /ruta/al/python-de-gaphor
bash test.sh --gaphor /ruta/a/gaphor
# Sin sesión gráfica, con Xvfb y xauth instalados:
bash test.sh --gaphor /ruta/a/gaphor --headless
```

## Límites del subconjunto

No incluye compuertas inclusivas, complejas o basadas en eventos; eventos de
borde, error, señal, compensación o transacción; subprocesos de evento;
coreografía; carriles anidados; objetos de datos; generación de código;
simulación; ni intercambio BPMN XML. La asociación con anotaciones no conecta
con flujos en esta versión.

La validación comprueba reglas estructurales implementadas. No demuestra ausencia
de bloqueos, sincronización correcta en todos los caminos, terminación de ciclos
ni equivalencia con un proceso real. Un informe sin errores no certifica
conformidad completa con la norma.

## Archivos

| Archivo | Responsabilidad |
| --- | --- |
| `model.py` | Tipos persistentes, propiedad y compatibilidad de extremos |
| `operations.py` | Creación, borradores y actualización transaccional |
| `validation.py` | Diagnósticos de borrador y comprobaciones finales |
| `diagram.py` | Notación, conectores, agrupación, arrastre y copia |
| `language.py` | Lenguaje, toolbox y creación nativa de diagramas |
| `editor.py` | Edición de propiedades en GTK |
| `service.py` | Menú, selección, panel y validación por sesión |
| `tests/` | Modelo, diagramas, editor e integración en proyectos temporales |

Base técnica: [extensiones de lenguaje de Gaphor](https://docs.gaphor.org/en/latest/modeling_language.html)
y [puntos de extensión de plugins](https://docs.gaphor.org/en/latest/plugins.html).
Referencia de notación: OMG, [BPMN 2.0.2](https://www.omg.org/spec/BPMN/2.0.2/),
documento normativo formal/2013-12-09. El alcance de este plugin se limita a lo
descrito y probado en esta documentación.
