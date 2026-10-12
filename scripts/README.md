# Carpetas → diagrama de paquetes

Para la consola de **Gaphor 3.3.2**: menú **Herramientas → Consola**.
El script vive en Git junto al modelo; no requiere instalar un plugin.

## Cargar el script

Ejecuta estas líneas en la consola, sustituyendo la ruta por la de tu equipo:

```python
import runpy
script = runpy.run_path(r"/home/ornonsu/Projects/exotic_ws/exotic-app-architecture/scripts/folder_to_diagram.py")
import_folder = script["import_folder"]
```

En Windows utiliza, por ejemplo, `r"C:\Users\tu_usuario\Desktop\exotic_ws\exotic-app-architecture\scripts\folder_to_diagram.py"`.

## Crear un diagrama

```python
import_folder(service, r"/ruta/absoluta/TransaccionesAlmacen", mode="new", name="Almacén", parent="Exotic-App")
```

Resultado en el árbol del modelo:

```text
Exotic-App                         paquete existente
└── Almacén                        paquete padre nuevo
    ├── Almacén                    diagrama nuevo
    └── TransaccionesAlmacen       paquete de la carpeta
        ├── index.jsx             artefacto
        └── components            subpaquete
            └── Tabla.jsx         artefacto
```

En el lienzo, `TransaccionesAlmacen` aparece como un paquete gráfico que contiene
las cajas de archivos y subcarpetas, con anidación real. El diagrama y el paquete
de contenido son hijos del mismo paquete padre; los elementos pertenecen a paquetes.

`name` toma el nombre de la carpeta si se omite. `parent` es opcional cuando
hay un solo paquete raíz; con un modelo vacío se crea el paquete padre en la raíz.

## Insertar en un diagrama existente

Consulta los destinos del modelo abierto:

```python
script["list_targets"](service)
```

Usa su ID, su ruta completa o un nombre que no se repita:

```python
import_folder(service, r"/ruta/absoluta/Proveedores", mode="existing", diagram="Exotic-App/Almacén/Almacén")
```

El diagrama debe pertenecer a un paquete UML. Se agrega el paquete `Proveedores`
bajo ese padre y se dibuja a la derecha del contenido actual, sin moverlo.

## Alcance

- Lee nombres y estructura, no contenidos. Conserva nombres y extensiones.
- Incluye carpetas vacías y archivos ocultos; omite enlaces y junctions.
- Opcional: `exclude=(".git", "node_modules")` excluye esos nombres en cualquier nivel.
- Máximo predeterminado: 1000 archivos/carpetas, ajustable con `max_items`; profundidad máxima: 60.
- Devuelve el inventario creado y las rutas omitidas. Cada ejecución importa una
  instantánea: no sincroniza ni reemplaza elementos. Rechaza destinos ambiguos o
  nombres de paquetes que colisionen; permite artefactos homónimos en carpetas distintas.
- Abre el diagrama y permite **Deshacer** la importación completa. Guarda tú con
  **Ctrl+S** después de revisar el resultado; el script no escribe el `.gaphor` en disco.

Referencias: [scripting](https://docs.gaphor.org/en/latest/scripting.html) y
[estilos](https://docs.gaphor.org/en/latest/style_sheets.html).
