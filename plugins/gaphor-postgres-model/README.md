# Modelo relacional PostgreSQL 0.1.0

Plugin independiente para **Gaphor 3.3.2**. Permite diseñar manualmente tablas y relaciones PostgreSQL con notación pata de gallo. No se conecta a una base de datos ni genera o ejecuta SQL.

**Los modelos que contengan elementos PostgreSQL necesitan este plugin para abrirse.** Se guardan tipos propios en el archivo `.gaphor`, incluidos sus referencias, diagramas y propiedades. Mantén el plugin versionado junto al proyecto.

## Empezar

1. Reinicia Gaphor y selecciona **PostgreSQL** en el selector de lenguaje.
2. Abre **Tools → Custom tools → Modelo relacional → Nuevo diagrama relacional…**. Se crea una base de datos, el esquema `public` y un diagrama. El menú nativo **New Diagram → Diagrama relacional** también está disponible.
3. Usa **Tabla** en la caja de herramientas. Selecciónala y pulsa **Editar tabla…** en el panel lateral o en el submenú anterior. El editor permite añadir columnas, claves, CHECK e índices.
4. Usa **Clave foránea (origen → destino)**: arrastra desde la tabla que contiene la FK hasta la tabla referenciada. Se abre el editor para elegir las correspondencias. Guarda primero la FK en el borrador y después la tabla. Cancelar cualquiera de esos pasos no crea una FK incompleta.
5. **Guardar** en el editor aplica una transacción al modelo en memoria. **Ctrl+S** guarda el archivo.

La herramienta **Esquema** crea otro esquema de la misma base de datos. Una tabla dibujada dentro de un esquema pertenece a él; fuera de un esquema gráfico se asigna al esquema predeterminado. Arrastra elementos existentes desde el árbol para representarlos en otros diagramas sin duplicarlos.

```text
BaseDatos
├── public
│   └── productos
│       ├── id: bigint [PK, NOT NULL]
│       ├── nombre: text
│       └── productos_pk
└── Diagrama relacional
```

**Doble clic** conserva el editor **Propiedades** del plugin existente, con Descripción, Nota, Diagramas y CSS. El editor relacional se abre mediante **Editar tabla…**. F2 conserva la edición nativa del nombre.

## Qué se puede especificar

| Elemento | Datos |
|---|---|
| Columna | Nombre, tipo libre con sugerencias, NULL/NOT NULL, DEFAULT e identidad `NONE`, `ALWAYS` o `BY DEFAULT` |
| PK / UNIQUE | Nombre, columnas ordenadas, claves compuestas y `NULLS NOT DISTINCT` para UNIQUE |
| FK | Tabla destino, pares ordenados de columnas, `ON DELETE` y `ON UPDATE` |
| CHECK | Nombre y expresión SQL |
| Índice | Nombre, método, UNIQUE, `NULLS NOT DISTINCT`, columnas o expresiones ordenadas, INCLUDE y WHERE |

Las tablas muestran nombre, tipos y marcas PK, FK, UQ y NOT NULL. Las opciones avanzadas permanecen en el editor. Se admiten tablas sin PK, relaciones autorreferenciales, varias FK entre las mismas tablas y relaciones entre esquemas de una misma base de datos. Para muchos-a-muchos se modela una tabla intermedia.

Los valores iniciales son `public`, `MATCH SIMPLE`, `NO ACTION`, B-tree y nulos distintos en UNIQUE. La cardinalidad del extremo referenciado es `0..1` si alguna columna local permite NULL y `1` en otro caso. El extremo que referencia es `0..1` si sus columnas contienen una clave única completa y `0..*` en otro caso. Las marcas pertenecientes a claves compuestas describen participación en la clave, no unicidad individual.

## Validación y edición segura

- El borrador permanece separado del modelo hasta Guardar. Un error conserva el editor y revierte la transacción completa. Deshacer/rehacer incluye los cambios de estructura y sus representaciones creadas.
- Se comprueban nombres, pertenencia y orden de columnas, claves únicas de destino, restricciones entrantes e incompatibilidades estructurales de índices. PK e identidad fuerzan NOT NULL.
- Las referencias apuntan a objetos: renombrar una tabla o columna conserva las FK. DEFAULT, CHECK y expresiones de índices son texto: no se reescriben. Se informa que deben revisarse.
- **Validar base de datos** comprueba también cambios hechos con los controles nativos de Gaphor. El editor de tablas es el acceso recomendado para cambios estructurales.
- El borrado nativo de una tabla, columna o clave utilizada queda bloqueado. El panel lateral indica qué referencias deben resolverse. En el editor se puede quitar una columna junto con las restricciones locales que la utilizan; una FK entrante debe modificarse primero en su tabla de origen.
- Las diferencias de tipos de una FK y acciones como SET NULL sobre NOT NULL generan advertencias. La compatibilidad real de tipos personalizados, operadores, extensiones y expresiones debe comprobarse en PostgreSQL.

La validación **no certifica el SQL ni sustituye a PostgreSQL**. La versión no incluye vistas, triggers, particionado, migraciones, importación, conexión ni generación SQL.

## Copiar, pegar y documentación

El pegado como vínculo reutiliza las tablas existentes. El pegado completo crea objetos nuevos y remapea columnas, claves e índices; añade sufijos a nombres de tablas e índices cuando sea necesario. Si una FK referencia una tabla no copiada, se conserva la referencia existente en el mismo modelo.

Al pegar entre proyectos, las dependencias deben estar incluidas: copiar la base de datos completa es la opción más sencilla. Si faltan referencias, la operación se revierte y aparece una indicación; no se enlaza por coincidencias de nombres.

Propiedades 0.3.0, importador 0.1.1 y Copiar referencias 0.1.0 conservan sus versiones y comportamientos. Este plugin no modifica `ExoticApp.gaphor`. Las tablas de Exotic se incorporan después, manualmente.

## Instalación en Windows

Gaphor usa su propio intérprete; no se crea un entorno Python por plugin. Para empaquetar se necesita un Python con pip, setuptools >= 68 y wheel disponibles. Desde esta carpeta:

```powershell
.\install.ps1 -PythonExe 'C:\ruta\a\python.exe'
.\test.ps1 -Installed
```

Destino predeterminado: `%USERPROFILE%\.local\gaphor\plugins-2`. El instalador no descarga dependencias, no modifica la instalación de Gaphor y retira únicamente metadatos antiguos de esta distribución. Reinicia Gaphor después de instalar.

## Instalación y pruebas en Linux

**Pendiente de ejecución en Linux.** Los scripts están preparados para una instalación nativa de Gaphor 3.3.2 con Python >= 3.12 y GTK disponibles; no se ha verificado Flatpak.

```bash
bash install.sh --python /ruta/al/python-de-gaphor
bash test.sh --gaphor /ruta/a/gaphor --installed
# Sin sesión gráfica: requiere Xvfb, xvfb-run y xauth instalados.
bash test.sh --gaphor /ruta/a/gaphor --installed --headless
```

Destino: `GAPHOR_PLUGIN_PATH` o `~/.local/gaphor/plugins-2`. El instalador comprueba la versión de Gaphor del intérprete seleccionado y no instala dependencias adicionales. Las pruebas de coexistencia necesitan las carpetas de los otros tres plugins en el mismo repositorio; `--installed` requiere que estén instalados.

## Desarrollo

| Archivo | Responsabilidad |
|---|---|
| `model.py` | Tipos persistentes, referencias y cardinalidades |
| `validation.py` | Validación estructural de borradores |
| `operations.py` | Borradores y transacciones de edición |
| `diagram.py` | Figuras, conexiones, agrupación, borrado y copia |
| `language.py` | Lenguaje, herramientas y creación nativa |
| `editor.py` | Ventanas y controles GTK |
| `service.py` | Sesión, menú, selección, panel lateral y refresco |

La persistencia y las presentaciones usan los puntos de extensión de Gaphor. El servicio instala además una adaptación pequeña en memoria del pegado nativo para presentar los errores de referencias como notificaciones; restaura el método al cerrar la última sesión. No se cambian los archivos de Gaphor, el mecanismo de copia ni la hoja de estilo del usuario.

Las pruebas generan modelos y capturas en una carpeta temporal cuya ruta muestran al terminar. Nunca utilizan `ExoticApp.gaphor` como archivo de salida. Los mensajes de rollback de los casos negativos son esperados; el resultado se determina por las aserciones y los archivos `*-status.txt`.

Fuentes de diseño: [extensiones de lenguaje de Gaphor](https://docs.gaphor.org/en/latest/modeling_language.html), [restricciones de PostgreSQL 18](https://www.postgresql.org/docs/18/ddl-constraints.html) e [índices de PostgreSQL 18](https://www.postgresql.org/docs/18/sql-createindex.html).
