# Análisis de los plugins existentes

Inspección de fuentes y metadatos locales realizada el 4 de noviembre de 2026.
El entorno encontrado es Windows con Gaphor 3.3.2; el ejecutable utiliza su
propio runtime Python 3.14.4. Las versiones siguientes corresponden a los
paquetes locales del repositorio y a los metadatos instalados consultados.

| Plugin | Versión | Responsabilidad | Aplicación al nuevo plugin |
| --- | --- | --- | --- |
| `gaphor-description-editor` | 0.3.0 | Descripción, nota, CSS y navegación hacia diagramas hijos mediante propiedades UML | Conservar su doble clic y sus propiedades; edición BPMN mediante acción y panel específicos |
| `gaphor-folder-diagram` | 0.1.1 | Representar carpetas y archivos como paquetes y artefactos UML | Referencia para creación transaccional y comprobación de disposición gráfica |
| `gaphor-copy-reference` | 0.1.0 | Copiar nombres y rutas desde menús contextuales | Referencia para servicios por sesión y limpieza de acciones |
| `gaphor-postgres-model` | 0.1.0 | Lenguaje relacional propio, tablas, claves, relaciones y editor | Antecedente para metamodelo, toolbox, figuras, conexiones y persistencia propias |

## Decisión de extensión

Se añade un paquete independiente, `gaphor-bpmn-model`, con namespace `BPMN`.
Se registran lenguaje, servicio por sesión y módulo de interfaz mediante los
entry points que ofrece Gaphor. No se convierten actividades UML en BPMN ni se
modifica el código de los plugins existentes.

El metamodelo mantiene referencias a objetos: la pertenencia al proceso, la
asignación de carril y los extremos de los flujos no dependen de los nombres
ni de la posición de las figuras. La composición se integra con la propiedad
nativa de Gaphor para conservar el árbol, la persistencia y la copia.

## Compatibilidad y comprobaciones necesarias

- Las extensiones de Gaphor son experimentales. Se limita inicialmente la
  dependencia a 3.3.2 y se comprueban las API con el runtime instalado.
- Los archivos `.gaphor` que incorporen tipos BPMN necesitarán este plugin
  al abrirse. Guardar el paquete junto al proyecto forma parte de su conservación.
- `GAPHOR_PLUGIN_PATH` añade ubicaciones de búsqueda; no oculta necesariamente
  los plugins del usuario. Las pruebas deben controlar los lenguajes cargados.
- Deben verificarse guardado/reapertura, copiar/pegar, conexiones, deshacer,
  agrupación y coexistencia con los cuatro plugins existentes. El resultado
  efectivo de esas verificaciones se registra en `VERIFICATION.md`.
- La interfaz de propiedades usa clases UML como base. La coexistencia debe
  comprobarse con objetos BPMN reales, sin suponerla por la herencia.

## Relación con el modelo arquitectónico

Se leyó `ExoticApp.gaphor`: utiliza formato 4 y contiene los diagramas
`Despliegue`, `ConfParamsCategoria` y `Productos Package Diagram`. No modela
los plugins ni contiene elementos BPMN. Crear el plugin no exige cambiar esas
decisiones. El archivo se preserva sin modificaciones; la incorporación de
procesos de Exotic a diagramas será un trabajo manual posterior del usuario.

## Referencias consultadas

- Documentación técnica oficial de Gaphor, [lenguajes de modelado](https://docs.gaphor.org/en/latest/modeling_language.html): registro y puntos de extensión.
- Documentación técnica oficial de Gaphor, [plugins](https://docs.gaphor.org/en/latest/plugins.html): entry points y ubicación de instalación.
- OMG, [BPMN 2.0.2](https://www.omg.org/spec/BPMN/2.0.2/), especificación normativa: base del subconjunto de notación; no se afirma conformidad completa.

La revisión describe las fuentes y el entorno observados; no certifica
compatibilidad con otras versiones de Gaphor, Linux o Flatpak.
