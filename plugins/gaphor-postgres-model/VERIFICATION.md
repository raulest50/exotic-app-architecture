# Verificación — 0.1.0

Entorno: Windows, ejecutable oficial de Gaphor 3.3.2, intérprete GTK incluido. Modelos temporales; `ExoticApp.gaphor` no se utiliza como fixture ni destino de escritura.

Verificado el **21 de octubre de 2026**: `test.ps1 -Installed` finalizó con PASS para las 44 pruebas, la integración desde fuentes y la integración del paquete instalado. Hay una única distribución `gaphor_postgres_model-0.1.0.dist-info` en la carpeta de plugins del usuario.

## Pruebas automatizadas

- **44 pruebas unitarias y de GTK**: columnas, tipos libres, claves simples/compuestas, cardinalidades, nulabilidad, identidad, CHECK, índices, INCLUDE, nombres, tablas sin PK, relaciones autorreferenciales y entre esquemas, dependencias entrantes, borrado protegido, copias profundas, referencias ausentes, serialización de booleanos, deshacer/rehacer, borradores obsoletos y cancelación.
- **Integración en dos sesiones reales**: selector PostgreSQL, menú, herramientas, editor, gesto de FK, cancelación, Guardar, undo/redo, portapapeles GTK, varias representaciones, guardar/reabrir, exportación PNG/SVG, temas claro/oscuro, zoom y convivencia con los tres plugins existentes.
- **Sin el plugin**: el cargador rechaza explícitamente el espacio de nombres PostgreSQL. Es la dependencia de formato acordada.
- **Regresiones existentes**: Propiedades **53**, importador **29**, Copiar referencias **24**; sus suites finalizaron correctamente y sus fuentes/versiones no se modificaron.
- **Inspección visual**: editor nativo redimensionable, tabla con PK/FK/NOT NULL y relación pata de gallo exportada con estilos claro y oscuro.

Las pruebas deliberadamente inválidas generan mensajes de rollback en el registro de Gaphor. Se comprueba que no dejen modificaciones parciales ni referencias colgantes.

## Instalación

La comprobación `test.ps1 -Installed` verifica los puntos de entrada reales y una única distribución instalada de cada versión: PostgreSQL 0.1.0, Propiedades 0.3.0, importador 0.1.1 y Copiar referencias 0.1.0.

## Límites comprobados y pendientes

- No se ejecutó SQL ni se consultó una base de datos. Las expresiones se guardan literalmente; la validación es estructural.
- La prueba visual automatizada usa ventanas y exportaciones temporales, no el modelo de trabajo del usuario.
- La prueba del portapapeles usa el bucle nativo GLib y espera a que termine cada operación antes de sustituir su contenido. Esto evita la reentrada y el reemplazo prematuro observados en el primer ejecutor de pruebas; el plugin conserva la copia nativa de Gaphor.
- Linux: scripts de instalación/prueba incluidos; **ejecución pendiente**. Flatpak y otras versiones de Gaphor no se verificaron.
- La incorporación del esquema real de Exotic al modelo queda para una edición manual posterior.
