# Copiar referencias

Plugin independiente **0.1.0** para **Gaphor 3.3.2**. Añade dos opciones al clic derecho de figuras y elementos del árbol:

- **Copiar nombre**: `FichaTecnicaMaterialCard.tsx`.
- **Copiar ruta relativa**: `Productos/Basic/componentes/FichaTecnicaMaterialCard.tsx`.

Copia texto plano y muestra **Copiado** mediante las notificaciones de Gaphor. Actúa sobre el elemento del clic derecho aunque hubiera otro seleccionado. Conserva las opciones originales y el comportamiento nativo de **Ctrl+C**.

## Cómo se determina la ruta

Se recorren los **paquetes que contienen gráficamente la figura en el diagrama activo**, desde el exterior hasta el archivo, separados por `/`. Se incluye el paquete exterior. Se conservan nombres, extensiones, espacios, mayúsculas y Unicode. El zoom y el desplazamiento no cambian la ruta.

Los ancestros del árbol que no contienen gráficamente la figura no se incluyen. No se filtra ningún nombre: un paquete `elements` se incluye si aparece como contenedor en el dibujo. Los componentes y otros contenedores que no sean paquetes tampoco añaden segmentos. Sin paquetes contenedores, la ruta es el nombre del elemento.

La ruta describe la organización del diagrama; **no comprueba archivos ni carpetas del repositorio**.

Desde el árbol, **Copiar nombre** funciona aunque no haya diagrama abierto. Para copiar la ruta, el elemento debe aparecer en el diagrama activo. Si no aparece o sus representaciones tienen rutas diferentes, se muestra una indicación para usar la figura correspondiente y se conserva el portapapeles. Varias representaciones con la misma ruta son válidas.

Al ejecutar la acción se vuelve a comprobar el elemento, su nombre, la figura y sus contenedores. No se copian referencias eliminadas ni nombres vacíos; un contenedor sin nombre también impide formar una ruta. Si cambia el diagrama mientras está abierto un menú del lienzo, hay que abrir nuevamente ese menú.

## Instalación

El código queda versionado aquí; la instalación es **por usuario de Gaphor**, disponible para todos sus proyectos. No modifica Gaphor ni añade información a los archivos `.gaphor`. Propiedades **0.3.0** e importador **0.1.1** se mantienen independientes.

Windows, desde esta carpeta, con Python 3.12 o posterior, pip y setuptools>=68:

```powershell
.\install.ps1 -PythonExe 'C:\ruta\python.exe'
```

Por defecto instala en `%USERPROFILE%\.local\gaphor\plugins-2`. Para una ruta personalizada usa `-PluginDirectory`. El script retira únicamente metadatos antiguos de **este** plugin tras instalar correctamente; conserva los demás complementos.

Linux, desde esta carpeta:

```bash
python3 -m pip install --no-deps --upgrade --target "$HOME/.local/gaphor/plugins-2" .
```

No se instala otra copia de Gaphor. Para un directorio de plugins personalizado, utiliza el que Gaphor tenga configurado mediante `GAPHOR_PLUGIN_PATH`. En Flatpak, la ruta debe ser accesible desde su entorno. **Linux está pendiente de ejecución y verificación.** Al actualizar, debe quedar un solo `gaphor_copy_reference-<versión>.dist-info`; no retires metadatos de otros plugins.

**Reinicia Gaphor** para cargar el complemento. Para desactivarlo, con Gaphor cerrado mueve fuera de la carpeta de plugins `gaphor_copy_reference` y `gaphor_copy_reference-0.1.0.dist-info`. El modelo no requiere cambios ni migraciones.

## Código

- `gaphor_copy_reference/paths.py`: cálculo y validación de referencias, sin escritura en el modelo.
- `gaphor_copy_reference/__init__.py`: servicio por sesión, acciones, adaptadores de menús, portapapeles y notificaciones.
- `tests/`: pruebas con modelos temporales; ninguna abre `ExoticApp.gaphor`.

El plugin adapta en memoria `modelbrowser.popup_model` y `diagrampage.context_menu_controller`. En el lienzo mantiene el menú nativo y su hit testing; añade las acciones **antes de abrir el popover**, porque GTK puede terminar el gesto al abrirlo. Las acciones transportan identificadores del elemento, figura, diagrama y sesión; no dependen de una selección global. Al cerrar un servicio se retiran sus opciones y se restauran sus controladores; al cerrar el último se restituyen las funciones originales. Otras versiones de Gaphor no se adaptan automáticamente.

## Verificación

```powershell
.\test.ps1
# Comprueba además las versiones instaladas y los tres plugins juntos:
.\test.ps1 -Installed
```

La suite cubre nombres completos, Unicode, anidamiento gráfico frente al modelo, varios paquetes exteriores, figuras sueltas, duplicados, nombres actualizados, figuras/elementos eliminados, rutas ambiguas, portapapeles real de GTK, conservación del modelo serializado y restauración de menús.

La integración usa dos sesiones nativas con identificadores iguales para comprobar aislamiento, hit testing real con otra figura seleccionada, callback de Ctrl+rueda, desplazamiento, refresco CSS y coexistencia con Propiedades e importador. También comprueba que las entradas estén listas antes de mostrar el menú. Los informes quedan en la carpeta temporal que indica el comando.

Se realizó además una prueba visual en Windows sobre un modelo temporal: menú del lienzo, ruta copiada y menú del árbol con copia del nombre, conservando las opciones nativas. Los modelos existentes no se modifican.

Resultado de entrega, 14 de octubre de 2026: **24 pruebas del plugin aprobadas**, integración de código fuente e instalación aprobadas, más **53 pruebas de Propiedades y 29 del importador** sin regresiones. Se verificó una sola distribución instalada de cada plugin y que el código de los dos complementos anteriores conserva sus hashes. `ExoticApp.gaphor` conserva su hash previo a este trabajo. Linux sigue pendiente.
