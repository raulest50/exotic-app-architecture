# Conexiones ortogonales 0.1.0

Plugin independiente para **Gaphor 3.3.2** (Python 3.12 o posterior).

Activa **Tools → Custom tools → Conexiones ortogonales** y selecciona
**Dependencia** (Shift+D). Arrastra desde el origen hasta el destino:

- **Espacio**, sin soltar el ratón: fija el trazado hasta ese punto.
- **Tab**: alterna horizontal/vertical primero para el tramo pendiente.
- **Escape**: cancela. Soltar fuera de un destino compatible también cancela.
- Suelta sobre otro elemento para confirmar. La flecha apunta al destino.

El modo comienza desactivado en cada sesión y no cambia otras relaciones.
Los puntos de paso permiten dirigir manualmente la conexión; no se evitan
obstáculos automáticamente. Las teclas se capturan solo durante el arrastre.
El origen y el destino deben ser figuras UML distintas, no otras líneas.
Se conserva la clasificación automática nativa de la herramienta Dependencia:
Gaphor puede elegir una relación más específica según los tipos de sus extremos.
Perder el foco, cambiar de diagrama o cerrar la vista cancela el dibujo.
La creación completa es una operación de deshacer/rehacer.

Se utilizan elementos, conexiones y coordenadas nativos. No se añaden perfiles
ni atributos personalizados. El archivo guardado se puede abrir y editar sin
este plugin. Guardar el archivo continúa siendo una acción normal de Gaphor.

## Instalación Windows

Cierra o reinicia Gaphor después de instalar. Desde esta carpeta, con un Python
que disponga de `pip` y `setuptools`:

```powershell
./install.ps1 -PythonExe 'C:/ruta/python.exe'
```

El destino predeterminado es `%USERPROFILE%/.local/gaphor/plugins-2`.
El instalador no modifica Gaphor ni otros plugins. Solo retira metadatos antiguos
de esta distribución tras comprobar que la instalación nueva existe.

## Instalación Linux

Con Gaphor 3.3.2 y Python compatible que disponga de `pip` y `setuptools`:

```sh
python3 -m pip install --no-deps --no-build-isolation --no-compile --upgrade \
  --target "$HOME/.local/gaphor/plugins-2" .
```

En instalaciones aisladas, usa la carpeta de plugins visible para esa instalación
de Gaphor (`GAPHOR_PLUGIN_PATH`). Linux está pendiente de ejecución; no se declara
verificado. Se reutiliza el submenú Custom tools si otros plugins lo crearon.

## Pruebas

```powershell
./test.ps1
./test.ps1 -Installed
```

Las pruebas ejecutan el runtime real de Gaphor con modelos temporales, sin abrir
ni modificar `ExoticApp.gaphor`. `tests/manual.py` abre una ventana independiente
para comprobar los gestos de ratón y teclado. Los registros van a la carpeta
temporal indicada por el ejecutor. Consulta `VERIFICATION.md` para los resultados.
