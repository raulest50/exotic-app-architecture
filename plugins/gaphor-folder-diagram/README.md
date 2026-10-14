# Importar/leer componente en crudo

Plugin independiente **0.1.1**, para **Gaphor 3.3.2**. Crea un diagrama de componentes a partir de los nombres de archivos y carpetas, sin leer su contenido ni inferir dependencias.

## Uso

1. Selecciona el paquete de destino y abre **Tools → Custom tools → Importar/leer componente en crudo…**.
2. Elige la carpeta origen y revisa el destino. También puedes elegir **Raíz del modelo**.
3. Ajusta las exclusiones y pulsa **Analizar**. El análisis se puede cancelar.
4. Revisa las cantidades y pulsa **Generar**. Se abrirá el diagrama ajustado a la vista.
5. Guarda el proyecto normalmente con **Ctrl+S**.

El destino inicial es el paquete más cercano al elemento enfocado. Si no hay figura enfocada, se usa el paquete del diagrama de la vista que emitió la selección. Si no hay vista o diagrama, se limpia la selección anterior y se propone **Raíz del modelo**.

Las exclusiones son nombres de carpetas, separados por comas, punto y coma o saltos de línea; se aplican a cualquier profundidad. No son rutas ni patrones glob. Inicialmente se excluyen `.git`, `node_modules`, `dist`, `build`, `.venv` y `__pycache__`. Vaciar el campo incluye todas las carpetas reales. Se incluyen archivos ocultos, archivos binarios y carpetas vacías. Los enlaces simbólicos, uniones y puntos de reanálisis no se recorren; se muestra cuántos se omitieron. Un error de acceso impide obtener una captura parcial.

Cambiar origen o exclusiones requiere analizar otra vez. **Generar** utiliza la captura de nombres del último análisis: si cambias archivos en disco después, vuelve a analizar para reflejar esos cambios.

## Modelo y disposición

Cada ejecución crea un paquete independiente `Lectura <carpeta>`, con un solo diagrama y un paquete `elements`. Dentro de `elements` queda el paquete de la carpeta raíz y su contenido anidado. Las repeticiones se numeran `(2)`, `(3)`, etc. No se sincronizan capturas anteriores.

En el dibujo solo aparecen la carpeta raíz y sus descendientes. Cada carpeta es un paquete UML y cada archivo un artefacto con nombre y extensión completos. Los nombres repetidos se distinguen por su paquete contenedor. El plugin distribuye primero archivos y después subcarpetas, alfabéticamente, en filas con 32 unidades de margen y al menos 24 entre hermanos. Mide los títulos y dimensiona los contenedores desde los hijos hacia sus padres. Comprueba la geometría antes de confirmar.

La creación completa se puede deshacer/rehacer en una operación. Cancelar o un error de generación no dejan elementos parciales. Todo se guarda como UML nativo dentro del `.gaphor`; puede abrirse y editarse sin el plugin. El editor de Propiedades es independiente y también funciona sobre los elementos generados.

## Corrección 0.1.1

Se corrige el aviso inesperado que podía aparecer al hacer zoom o refrescar CSS sin figura enfocada. `DiagramSelectionChanged` proporciona el diagrama mediante `event.diagram_view.model`, no mediante `event.diagram`. Se conservan los identificadores, el menú y el comportamiento de generación. Propiedades no requiere cambios.

No se añade almacenamiento automático de logs. Los diagnósticos nativos de Gaphor permanecen en memoria durante la sesión y pueden guardarse manualmente mediante **About Gaphor → Troubleshooting → Debugging Information → Save As…** antes de cerrar la aplicación.

## Instalación

Requiere Python 3.12 o posterior para empaquetar; Gaphor ejecuta el plugin con su propio intérprete. Instala únicamente este paquete, sin instalar otra copia de Gaphor.

Windows, desde la carpeta del plugin (Python con pip y setuptools>=68):

```powershell
.\install.ps1 -PythonExe 'C:\ruta\python.exe'
```

El instalador Windows elimina, después de instalar correctamente, únicamente los metadatos de versiones anteriores de `gaphor-folder-diagram`. Esto evita registrar el servicio dos veces; no modifica otros plugins.

Linux, desde esta carpeta:

```bash
python3 -m pip install --no-deps --upgrade --target "$HOME/.local/gaphor/plugins-2" .
```

Al actualizar desde 0.1.0 en Linux, comprueba que solo quede `gaphor_folder_diagram-0.1.1.dist-info`: `pip --target` puede conservar `gaphor_folder_diagram-0.1.0.dist-info`, que debes retirar después de instalar correctamente. Conserva los metadatos de otros plugins.

Reinicia Gaphor después. La ruta de plugins se puede personalizar mediante `GAPHOR_PLUGIN_PATH`; en el instalador Windows utiliza `-PluginDirectory`. En Flatpak, Gaphor necesita acceso a la carpeta de plugins y al origen que quieras analizar. La ejecución en Linux queda pendiente de verificación.

Para desactivar, cierra Gaphor y mueve fuera de su carpeta de plugins `gaphor_folder_diagram` y `gaphor_folder_diagram-0.1.1.dist-info`. No borres los elementos del modelo: son documentos independientes del plugin. El código instalado de Gaphor no se modifica.

## Código y pruebas

- `gaphor_folder_diagram/__init__.py`: servicio, menú y selección por sesión.
- `ui.py`: diálogo y análisis en segundo plano.
- `scanner.py`: lectura del árbol de nombres, exclusiones y cancelación.
- `model.py`: creación UML, disposición y validación geométrica.
- `tests/`: modelos y carpetas temporales; ninguna prueba abre `ExoticApp.gaphor`.

```powershell
.\test.ps1
# Añade verificación de los plugins instalados y su coexistencia:
.\test.ps1 -Installed
```

Se verifican jerarquía, cinco archivos/dos carpetas, nombres largos, Unicode, carpetas vacías, exclusiones, errores, cancelación, lecturas repetidas, separación y contención, deshacer/rehacer, reapertura sin plugins y aislamiento de proyectos. También se usa el evento real `DiagramSelectionChanged` con figura enfocada, selección vacía y vista/diagrama ausentes, y se comprueba el destino al cambiar de diagrama. La integración de código fuente carga el editor desde la carpeta hermana `gaphor-description-editor`. Los informes y un PNG del ejemplo quedan en la carpeta temporal indicada al terminar.

### Verificación realizada — 14 de octubre de 2026

En Windows con Gaphor 3.3.2: **29 pruebas aprobadas** y reapertura/edición nativa sin plugins. Antes de corregir el código, la nueva prueba de selección vacía reprodujo el mismo `AttributeError` con el evento real. La integración usa vistas nativas, el callback real de Ctrl+rueda (con el modificador suministrado por la prueba), refresco CSS asíncrono y dos proyectos con Propiedades. No sustituye una prueba manual con el ratón.

`test.ps1 -Installed` comprueba además la versión 0.1.1 instalada, un único registro del servicio, el menú, la acción, el destino y la misma integración con Propiedades 0.3.0. En la entrega anterior se revisaron visualmente el PNG del ejemplo, el menú y la apertura del diálogo.

La prueba visual completa del selector nativo y del flujo hasta Generar quedó pendiente: la herramienta de control de ventanas devolvió `failed to activate captured window` al intentar interactuar con el diálogo modal. La selección/cancelación, generación y ajuste de vista sí tienen comprobaciones automatizadas; estas no sustituyen esa prueba manual. Linux también está pendiente de ejecución.
