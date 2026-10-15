# Instrucciones para agentes — arquitectura

Este repositorio contiene el modelo arquitectónico de Exotic y sus plugins de
Gaphor. Esta metodología también aplica a los repositorios hermanos
`exotic-app-frontend`, `exotic-app-backend` y `exotic-app-e2e`.

## Propósito: reducir tres deudas

El repositorio de arquitectura tiene como propósito reducir la deuda técnica,
la deuda cognitiva y la deuda de intención. En esta metodología:

- **Deuda técnica:** dificultades para mantener y evolucionar el código por
  complejidad innecesaria, acoplamiento o decisiones estructurales pendientes.
  El modelo debe ayudar a identificar y orientar mejoras en la implementación;
  documentar un problema no lo resuelve por sí solo.
- **Deuda cognitiva:** esfuerzo acumulado para comprender el sistema, localizar
  responsabilidades y anticipar el impacto de un cambio. Las vistas simples y
  congruentes deben facilitar esa comprensión a personas y agentes.
- **Deuda de intención:** pérdida o ambigüedad sobre qué se quiere conseguir,
  por qué se tomó una decisión y qué responsabilidades y límites debe respetar
  la implementación. Conservar esa intención en las descripciones y relaciones
  relevantes, distinguiendo el comportamiento actual del objetivo acordado.

Evaluar cada detalle del modelo por cuánto ayuda a comprender, decidir o
mantener la congruencia, considerando también su costo de actualización.
Mantenerlo simple e incremental es parte de este propósito.

## Fuente de verdad y alcance

- `ExoticApp.gaphor` es la fuente de verdad de las decisiones arquitectónicas
  explícitamente modeladas: estructura, archivos cuando se representan como
  artefactos, responsabilidades, relaciones y especificaciones asociadas.
- El código debe ser congruente con esas decisiones. El modelo expresa la
  arquitectura acordada; revisar el código permite comprobar su implementación.
  Una discrepancia debe resolverse explícitamente, no ocultarse cambiando el
  modelo para justificar el código ni ignorando el modelo.
- El modelado es incremental, por módulo, pestaña o aspecto. Si no existe un
  diagrama aplicable, continuar con las convenciones del código y la solicitud
  del usuario. No exigir crear diagramas para toda la aplicación ni ampliar el
  alcance del modelado por iniciativa propia.
- Mantener el modelo más simple que el código. Elegir solo las vistas útiles;
  no imponer todas las vistas 4+1, diagramas de clases, procesos ni generación
  de código. Omitir detalles deliberadamente es válido.
- La ausencia de un detalle o una flecha no implica una prohibición. Verificar
  lo que el modelo especifica y su alcance, sin inferir contratos inexistentes.
  Los detalles no modelados pueden resolverse en código sin añadir diagramas,
  siempre que respeten las decisiones explícitas y las reglas sobre archivos.

## Consulta antes de implementar

1. Leer la versión local guardada de `ExoticApp.gaphor`, incluidos los cambios
   locales del usuario. Identificar los diagramas y elementos del alcance
   afectado, su pertenencia, relaciones, notas y descripciones relevantes.
2. Compararlos con el código que se modificará. Distinguir discrepancias previas
   de los cambios propuestos; no reparar ni revertir diferencias por iniciativa
   propia. Si afectan a la decisión de implementación, explicar la diferencia y
   consultar al usuario antes de modificar esa parte.
3. Si falta el repositorio o no se puede leer el modelo, declarar la limitación
   y pedir acceso o la aclaración necesaria para decisiones dependientes de él.
   Continuar el trabajo independiente. No afirmar que no hay diagrama sin
   haberlo comprobado; los cambios sin guardar en Gaphor no son visibles en disco.

## Control de archivos y cambios arquitectónicos

- Antes de crear, eliminar, renombrar o mover archivos persistentes en cualquiera
  de los cuatro repositorios, avisar con las rutas concretas, el motivo y los
  diagramas afectados, o indicar que no se encontró un diagrama aplicable.
  Incluir código, pruebas, configuración, scripts y documentación.
- Si la solicitud no autoriza ya esa operación concreta, pedir autorización
  explícita antes de ejecutarla. No repetir la pregunta si ya fue autorizada en
  la conversación. Una petición genérica de implementar o refactorizar no basta
  para decidir silenciosamente una nueva estructura de archivos.
- Preparar primero una propuesta concreta y continuar lo que no dependa de esa
  autorización. Favorecer cambios en archivos existentes cuando sean coherentes;
  no concentrar responsabilidades incompatibles solo para evitar nuevos archivos.
- Los artefactos temporales de herramientas, cachés y salidas de compilación no
  forman parte de este inventario arquitectónico; evitar su versionado accidental.
- Aunque no cambien los archivos, avisar si cambian responsabilidades, dependencias,
  límites de módulos o comportamiento especificado en el modelo. Una decisión
  contraria a lo modelado requiere acuerdo explícito antes de implementarla.
- El usuario mantiene manualmente los diagramas. No editar, regenerar ni
  sobrescribir `ExoticApp.gaphor` sin petición explícita. La autorización para
  cambiar código no autoriza modificar el modelo.

## Sincronización y entrega

- Para cada cambio, revisar la congruencia del alcance modelado y entregar una
  lista breve y concreta de actualizaciones manuales: artefactos que añadir o
  retirar, rutas o paquetes que cambiar, relaciones y descripciones que ajustar.
  Si no hay impacto en lo modelado, indicarlo sin inventar cambios visuales.
- Identificar los archivos por su repositorio y ruta relativa, conservando
  subcarpetas, nombres y extensiones. No confundir elementos homónimos.
- Los paquetes y carpetas organizadores del árbol de Gaphor, como `elements`,
  no equivalen automáticamente a carpetas del código. Una figura tampoco implica
  por sí sola un archivo: esa correspondencia aplica a los artefactos del
  inventario de archivos, como los representados en Productos.
- Una implementación entregada con cambios manuales pendientes debe declararse
  **pendiente de sincronización con Gaphor**. No afirmar que modelo y código están
  sincronizados hasta revisar el modelo actualizado. Esta revisión complementa,
  no sustituye, las validaciones técnicas del repositorio correspondiente.

## Trabajo en este repositorio

- Preservar los cambios locales del modelo y de los plugins. Para verificaciones
  que necesiten escribir modelos, usar modelos temporales; no usar
  `ExoticApp.gaphor` como archivo de prueba.
- Mantener cada plugin en su propia carpeta de `plugins/` y consultar sus
  instrucciones de instalación y verificación cuando el trabajo lo afecte.
- No instalar plugins ni ejecutar suites de pruebas como consecuencia de una
  modificación exclusiva de estas instrucciones.
