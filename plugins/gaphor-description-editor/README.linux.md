# Instalación en Kali Linux

Soporte para la instalación nativa de Gaphor **3.3.2**. Se utilizan el mismo
código Python, empaquetado y pruebas que en Windows. Los archivos de Windows
se conservan sin cambios. Estos scripts no gestionan instalaciones Flatpak.

## Requisitos

- Python **3.12 o posterior**, en el entorno donde está instalado Gaphor 3.3.2.
- `pip`, `setuptools>=68` y `wheel` disponibles en ese Python.
- Para las pruebas: Bash y `timeout`; sin pantalla gráfica, también `xvfb-run`,
  `Xvfb` y `xauth`.

## Instalar o actualizar

Desde esta carpeta:

```bash
bash install.sh
```

Se instala únicamente el plugin en `~/.local/gaphor/plugins-2`. El instalador
usa una copia temporal para empaquetarlo, sin descargar dependencias ni
modificar las fuentes o la instalación de Gaphor. No requiere `sudo`.
Para actualizarlo después de un pull, repite el comando y reinicia Gaphor.

Opciones para otra instalación nativa o carpeta de plugins:

```bash
bash install.sh --python /ruta/al/python/de/gaphor
GAPHOR_PLUGIN_PATH=/ruta/a/plugins bash install.sh
```

También existe `--plugin-directory /ruta/a/plugins`. Si cambias el destino,
usa ese mismo `GAPHOR_PLUGIN_PATH` al iniciar Gaphor y al ejecutar las pruebas.

Tras reiniciar Gaphor, selecciona un elemento UML y usa **Tools → Editar
descripción**, **Ctrl+Alt+D** o doble clic en su figura. Guarda los campos y
después el proyecto con **Ctrl+S**. Consulta [README.md](README.md) para los
detalles del editor y del almacenamiento UML compartido entre plataformas.

## Verificar

```bash
# Pruebas del código fuente y reapertura sin plugin:
bash test.sh

# Añadir integración del paquete instalado:
bash test.sh --installed

# Forzar una pantalla virtual o elegir otro ejecutable:
bash test.sh --installed --headless --gaphor /usr/bin/gaphor
```

Sin `DISPLAY` ni `WAYLAND_DISPLAY` se usa automáticamente una pantalla virtual.
Cada proceso tiene un límite de 30 segundos. Las pruebas reutilizan los cuatro
archivos Python existentes y comprueban sus informes de estado además de la
salida del proceso. Los resultados y modelos temporales se conservan en la
carpeta indicada al comenzar; no se abre ni modifica `ExoticApp.gaphor`.

La integración comprueba la carga del plugin, menú, acelerador, panel, guardado
y aislamiento entre dos sesiones. La pantalla virtual permite comprobar GTK,
pero no sustituye la comprobación visual y de atajos en el escritorio real.

Verificado el **14 de octubre de 2026** en Kali Linux con Gaphor **3.3.2** y
Python **3.14.6**: instalación local del paquete **0.1.0**, **19 pruebas
aprobadas**, reapertura y edición sin plugin, e integración del paquete instalado
aprobada con `bash test.sh --headless --installed`. La verificación con GTK se
ejecutó fuera del sandbox de Codex, que restringía el acceso a la pantalla virtual.

## Desactivar

Con Gaphor cerrado, mueve fuera de su carpeta de plugins los directorios
`gaphor_description_editor` y `gaphor_description_editor-0.1.0.dist-info`.
Las descripciones permanecen en el modelo y se pueden consultar mediante
las propiedades nativas del estereotipo `Describible`.
