# Verificación 0.1.0

Fecha: 2026-10-14. Windows, Gaphor 3.3.2.

- **22 pruebas del plugin: PASS.** Geometría, puntos fijos, retrocesos,
  repetición de teclas, cancelación, recuperación de selección, errores,
  dirección, zoom, anidamiento, sesiones independientes y versiones incompatibles.
- **Integración de código fuente e instalación: PASS.** Acciones nativas de menú,
  dos sesiones, artefactos/componentes/paquetes, Propiedades 0.3.0, importador
  0.1.1, refresco CSS y zoom. Restauración del método original al cerrar servicios.
- **Reapertura en otro proceso sin plugins: PASS.** Puntos y extremos nativos
  conservados; el modelo se vuelve a guardar mediante Gaphor sin el plugin.
- **Regresión:** 53 pruebas de Propiedades y 29 del importador aprobadas.
- **Interfaz Windows:** menú activado con clics, dependencia trazada con arrastre
  real, flecha en destino, deshacer/rehacer con botones y cancelación al soltar
  en vacío. El lienzo y los datos usados fueron temporales.

Las señales `key-pressed`/`key-released` de Espacio y Tab se comprobaron en
controladores GTK reales, también durante un arrastre de ratón real en la
ventana de prueba. La herramienta de automatización no permite mantener el
botón del ratón mientras envía una tecla física por separado; esa combinación
física queda pendiente de comprobación manual. El modo opcional de inyección
solo existe en `tests/manual.py`, nunca en el plugin instalado.

Linux está pendiente de ejecución. No se cambiaron los archivos de los otros
plugins ni se abrió/escribió `ExoticApp.gaphor` desde las pruebas.

## Registros locales de esta ejecución

- Instalación e integración: `%TEMP%/gaphor-orthogonal-tests-b39bbd81-c211-4bd0-9171-1244cf7f290d/`.
- Propiedades: `%TEMP%/gaphor-description-tests-abf82d12-e413-4c20-ac05-92dcc03994a2/`.
- Importador: `%TEMP%/gaphor-folder-tests-6499d2e6-51f5-4cef-8330-88ccf184383a/`.
- Interfaz: `%TEMP%/gaphor-orthogonal-ui-a764426d-4ac6-4d66-ab14-7e83df9cbb17/`.

Las carpetas temporales son evidencia local de esta ejecución, no requisitos
del plugin. `test.ps1` genera nuevas carpetas en cada ejecución.
