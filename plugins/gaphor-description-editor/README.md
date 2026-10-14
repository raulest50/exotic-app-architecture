# Propiedades para Gaphor 3.3.2 — versión 0.2.0

Editor de **Descripción**, **Nota** y **Estilo CSS** para elementos UML. Los tres campos se conservan dentro del archivo `.gaphor`.

## Uso

1. Selecciona un elemento y pulsa **Ctrl+Alt+D**, elige **Tools → Propiedades…** o utiliza el botón **Propiedades…** del panel derecho. También puedes hacer doble clic en su figura.
2. En **Documentación**, edita Descripción y Nota. La ventana es redimensionable y el separador entre ambos campos es ajustable.
3. En **Estilo CSS**, escribe declaraciones, por ejemplo:

   ```css
   background-color: lightblue;
   color: navy;
   font-size: 18;
   ```

4. Pulsa **Guardar** y después guarda el proyecto normalmente (**Ctrl+S**).

El CSS corresponde al **elemento UML**: afecta a todas sus apariciones actuales y futuras, incluso en otros diagramas. Sus textos y detalles propios reciben el estilo; las figuras hijas y nietas conservan su estilo independiente. Dos elementos con el mismo nombre no comparten personalización.

Vaciar CSS restaura el estilo normal. No hay vista previa provisional. Un error de CSS impide guardar los tres campos y se muestra con línea y columna. **Cancelar**, **Esc** o cerrar no modifican el modelo. Guardar constituye una sola operación de deshacer/rehacer.

El panel conserva la vista breve de Descripción y el campo **Note** habitual. **F2** conserva la edición del nombre. Un doble clic en una referencia a otro diagrama sigue abriendo ese diagrama.

## CSS admitido

Se utiliza el analizador de Gaphor 3.3.2, con validación adicional. Es CSS de diagramas de Gaphor, no CSS de navegador.

- Colores: `background-color`, `color`, `text-color`.
- Texto: `font-family`, `font-size`, `font-style`, `font-weight`, `text-decoration`, `text-align`, `white-space`.
- Figura y disposición: `border-radius`, `dash-style`, `padding`, `justify-content`, `line-width`, `min-width`, `max-width`, `min-height`, `opacity`, `vertical-align`, `vertical-spacing`.

Admite colores con nombre, hexadecimales y funciones `rgb`, `rgba`, `hsl`, `hsla`; las medidas usan números sin unidad o `px`. El efecto de una propiedad depende de lo que dibuje cada tipo de figura. Por ejemplo, una relación puede utilizar el color y grosor de línea, pero no tener un fondo que rellenar. Los colores explícitos se mantienen en los temas claro y oscuro.

No admite selectores, bloques, directivas, variables, `!important`, propiedades exclusivas de diagramas (`line-style`) ni de pseudoelementos (`content`). El CSS personalizado tiene prioridad sobre las propiedades nativas correspondientes. La hoja global del modelo se conserva intacta y sigue definiendo las propiedades no personalizadas.

Si se introduce CSS inválido desde el editor nativo de estereotipos, se conserva el texto pero no se aplica; el registro de Gaphor informa del motivo. Abre Propiedades para ver el error al intentar guardar y corregirlo.

## Almacenamiento y compatibilidad

Las definiciones se crean al guardar el primer valor no vacío y se reutilizan:

```text
DocumentacionArquitectura (Profile)
  Element (metaclase)
  Describible (Stereotype que extiende Element)
    descripcion: String
    css: String
  String (PrimitiveType)
```

Cada atributo se añade cuando se necesita. Abrir modelos anteriores no los modifica; guardar CSS añade el atributo al perfil existente sin alterar descripciones ni notas. Guardar únicamente una nota no crea el perfil. Se utilizan objetos UML nativos, sin archivos laterales, y se conservan los identificadores de los valores al editarlos.

**Sin el plugin**, Descripción y CSS permanecen accesibles desde **Describible → descripcion / css**, pero el CSS no se aplica visualmente. Nota sigue siendo el campo nativo. La aplicación de CSS y la adaptación del doble clic existen solo en memoria y se retiran al cerrar las sesiones del plugin. Con el plugin activo, las exportaciones utilizan también los estilos personalizados.

Los nombres del perfil, estereotipo y atributos identifican el almacenamiento: no los renombres ni los borres si quieres conservar los datos. Ante duplicaciones o tipos incompatibles, el editor informa del conflicto sin sobrescribirlos. Si aparece `«Describible»` en las figuras, puede ocultarse con la opción nativa de mostrar estereotipos.

Se conservan el paquete `gaphor-description-editor`, el servicio `description_editor`, la acción `edit-description`, el atajo y la API `save_documentation`, que sigue editando solo documentación y preserva CSS. El importador de componentes continúa siendo un plugin separado.

## Instalación en Windows

Requiere Gaphor **3.3.2** y Python **3.12 o posterior** con `pip`, `setuptools>=68` y `wheel` disponibles para empaquetar. Desde esta carpeta:

```powershell
.\install.ps1 -PythonExe 'C:\ruta\a\python.exe'
```

Instala únicamente este plugin, sin descargar Gaphor ni dependencias, en `%USERPROFILE%\.local\gaphor\plugins-2`. Si usas `GAPHOR_PLUGIN_PATH`, pasa esa carpeta con `-PluginDirectory`. El instalador elimina solo los metadatos obsoletos de este mismo paquete tras instalar correctamente la nueva versión, evitando entradas duplicadas.

Reinicia Gaphor para cargar la actualización. Para desactivar, con Gaphor cerrado mueve fuera de la carpeta de plugins `gaphor_description_editor` y `gaphor_description_editor-0.2.0.dist-info`. No se modifica la instalación de Gaphor.

## Instalación en Linux — pendiente de ejecución

El código es compartido; no requiere una implementación distinta. Para una instalación nativa de Gaphor 3.3.2, después de obtener el repositorio con Git, ejecuta desde esta carpeta con un Python compatible y las herramientas de empaquetado disponibles:

```bash
python3 -m pip install --no-deps --no-build-isolation --no-compile --upgrade \
  --target "$HOME/.local/gaphor/plugins-2" .
```

Al actualizar desde 0.1.0, retira únicamente `gaphor_description_editor-0.1.0.dist-info` si permanece junto a los metadatos 0.2.0. Reinicia Gaphor. Flatpak puede utilizar una ubicación aislada distinta: comprueba su ruta de plugins antes de instalar. La instalación y ejecución en Linux no se han probado.

## Verificación

```powershell
.\test.ps1
# Incluye integración con el paquete instalado:
.\test.ps1 -Installed
# Si Gaphor está en otra ruta:
.\test.ps1 -GaphorExe 'D:\Gaphor\gaphor.exe'
```

Las pruebas usan el intérprete del Gaphor instalado y modelos temporales. No abren el modelo del repositorio. Los informes y una exportación PNG de un paquete con un artefacto de estilo independiente quedan en la carpeta temporal indicada al terminar.

Se verifican componentes, artefactos, paquetes, relaciones, nombres iguales, múltiples apariciones, hijos y nietos, textos largos, Unicode, validación, cancelación, transacciones, deshacer/rehacer, reapertura, modelos anteriores, ediciones nativas, temas claro/oscuro, hoja global, aislamiento de sesiones y restauración de los mecanismos originales. Otro proceso verifica lectura, edición y reapertura sin cargar el plugin.

Verificado el 14 de octubre de 2026 en Windows/Gaphor 3.3.2: 37 pruebas del editor, 24 del importador y las comprobaciones de instalación y reapertura sin plugins aprobadas. Se inspeccionaron visualmente la exportación PNG, los estilos independientes, la apertura por doble clic y Documentación. El control automático del modal devolvió `failed to activate captured window`: no se completó la comprobación manual de la pestaña CSS ni del arrastre del separador; sus widgets, validación y guardado se verificaron mediante GTK. Linux sigue pendiente de ejecución.

## Archivos y límites

- `gaphor_description_editor/__init__.py`: ventana, panel, accesos y doble clic.
- `gaphor_description_editor/model.py`: perfil UML, persistencia y transacción.
- `gaphor_description_editor/styles.py`: validación, cálculo aislado de estilos y actualización de vistas.
- `tests/`: pruebas automáticas e integración.
- `pyproject.toml`, `install.ps1`, `test.ps1`: empaquetado, instalación y ejecución de pruebas.

Texto plano y elementos UML; excluye estereotipos, que Gaphor no permite estereotipar. No añade campos a elementos C4 ni formas sin elemento UML. Limitado a Gaphor 3.3.2: otras versiones requieren verificar las API internas antes de habilitarlo.
