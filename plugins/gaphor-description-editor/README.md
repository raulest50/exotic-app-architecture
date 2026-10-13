# Editor de Descripción y Nota para Gaphor 3.3.2

Editor de texto plano para elementos UML. Mantiene **Descripción** y **Note** como campos independientes dentro del archivo `.gaphor`.

## Uso

1. Selecciona un elemento UML y pulsa **Ctrl+Alt+D**, o elige **Tools → Editar descripción**. También puedes hacer doble clic en su figura en el diagrama.
2. Edita **Descripción** y **Nota**. Amplía la ventana o arrastra el separador entre los campos.
3. Pulsa **Guardar** y después guarda el proyecto normalmente (**Ctrl+S**).

El panel derecho muestra una vista breve de Descripción y un botón para abrir el editor. El campo **Note** habitual sigue disponible. **F2** conserva el editor de nombre. Un doble clic en una referencia a otro diagrama sigue abriendo ese diagrama.

**Cancelar**, **Esc** o cerrar la ventana no cambian el modelo. Guardar ambos campos constituye una sola operación de deshacer/rehacer. Las notas anteriores no se copian a Descripción.

## Almacenamiento

Al guardar la primera descripción no vacía se crea, una sola vez por modelo:

```text
DocumentacionArquitectura (Profile)
  Element (metaclase)
  Describible (Stereotype que extiende Element)
    descripcion: String
  String (PrimitiveType)
```

Cada elemento documentado recibe una aplicación de `Describible` con su valor de `descripcion`. Solo se utilizan objetos UML nativos, sin formato privado ni archivos laterales. Guardar únicamente una nota no crea el perfil.

Sin el plugin, la descripción puede leerse y editarse desde la sección nativa de estereotipos: **Describible → descripcion**. No borres el perfil, su propiedad ni la aplicación del estereotipo si quieres conservar las descripciones. Si aparecen nombres `«Describible»` en las figuras, puedes ocultarlos con la opción nativa de mostrar estereotipos.

Los nombres del perfil, estereotipo y propiedad identifican el almacenamiento: no los renombres. Ante duplicaciones o tipos incompatibles, el editor informa del conflicto y no sobrescribe los datos.

## Instalación en Windows

Requiere Gaphor **3.3.2** y un Python **3.12 o posterior** con `pip`, `setuptools>=68` y `wheel` disponibles para empaquetar. Desde esta carpeta:

```powershell
.\install.ps1 -PythonExe 'C:\ruta\a\python.exe'
```

El script instala únicamente este plugin, sin descargar Gaphor ni sus dependencias, en `%USERPROFILE%\.local\gaphor\plugins-2`. Reinicia Gaphor. Si usas `GAPHOR_PLUGIN_PATH`, pasa esa carpeta mediante `-PluginDirectory`.

Para actualizar, repite la instalación. Para desactivar, con Gaphor cerrado mueve fuera de la carpeta de plugins `gaphor_description_editor` y su carpeta `gaphor_description_editor-0.1.0.dist-info`. El código de Gaphor instalado no se modifica; el doble clic se adapta únicamente en memoria mientras hay sesiones compatibles.

## Verificación

```powershell
.\test.ps1
# Añadir integración con el plugin ya instalado:
.\test.ps1 -Installed
# Si Gaphor está en otra ruta:
.\test.ps1 -GaphorExe 'D:\Gaphor\gaphor.exe'
```

Las pruebas ejecutan el intérprete del Gaphor instalado, con modelos temporales y una carpeta vacía de plugins. No abren el modelo del repositorio. Los informes quedan en la carpeta temporal indicada al terminar.

Comprueban componentes, artefactos, paquetes, dependencias, texto largo y Unicode, independencia de campos, cancelación, transacciones, deshacer/rehacer, reapertura, reutilización de identificadores, conflictos, selección y aislamiento de sesiones. Un segundo proceso, sin importar el plugin, comprueba lectura y edición mediante las propiedades nativas del estereotipo.

## Archivos y límites

- `gaphor_description_editor/__init__.py`: ventana, panel, accesos y adaptación de doble clic por sesión.
- `gaphor_description_editor/model.py`: persistencia mediante perfil UML y transacción.
- `tests/`: comprobaciones automáticas y reapertura sin plugin.
- `pyproject.toml`, `install.ps1`, `test.ps1`: empaquetado, instalación y ejecución de pruebas.

Primera versión: texto plano y elementos UML; excluye estereotipos, que Gaphor no permite estereotipar. No añade campos a elementos SysML, C4 ni formas sin elemento UML. La adaptación de la interfaz está limitada a Gaphor 3.3.2; otras versiones requieren verificar sus API antes de habilitarla.

Verificado el 13 de octubre de 2026 en Gaphor 3.3.2 para Windows: 19 pruebas automáticas aprobadas, reapertura/edición sin plugin y prueba de integración del paquete instalado con menú, acelerador, panel y dos sesiones. Se comprobó visualmente la apertura por doble clic y los dos campos. El arrastre manual del separador no pudo verificarse por una limitación del control de ventanas modales; su posición ajustable se comprobó mediante GTK.
