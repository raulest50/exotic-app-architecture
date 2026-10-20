# Productos: hallazgos y base para mejorar el modelo de recetas

**Estado:** documento de análisis y propuesta; no constituye una implementación ni un diseño aprobado.

**Preparado:** 20 de octubre de 2026. **Datos de producción analizados:** consulta de solo lectura del 14 de octubre de 2026. Las cifras describen esa consulta; no se ha vuelto a consultar producción para redactar este documento.

Documento ubicado en `exotic-app-architecture/Productos/temp.md` por indicación del usuario y referenciado por el artefacto `temp.md` del paquete Productos en Gaphor. La intervención comprende **1 archivo documental y su referencia en el modelo; 0 entidades de aplicación nuevas**. No modifica código de la aplicación, base de datos ni despliegues.

## 1. Intención y alcance

Mejorar integralmente el manejo de recetas, unidades, contenido y cantidades en Productos, conservando la estructura útil del módulo. Se admite evaluar una entidad adicional y algunos atributos; su necesidad debe justificarse antes de implementarlos.

Necesidades expresadas:

- Reutilizar un mismo granel en diferentes presentaciones sin crear códigos distintos para compensar diferencias de cálculo.
- Poder registrar los ingredientes para obtener **1 kg, 800 kg u otra cantidad explícita de salida**.
- Escalar los insumos según la cantidad solicitada por la OP u OF.
- Mantener separado el contenido por envase: por ejemplo, 450 ml por frasco.
- Mostrar claramente en el diseñador qué cantidad de producto genera la receta.
- Preservar el funcionamiento existente durante la transición.

Caso motivador: el cliente considera que `GR001`, `GRTP1`, `GR002` y `GRSCH1` representan la misma composición. `GRA1` tiene más agua y debe conservar su identidad; se excluyeron del análisis también los terminados que lo consumen.

La mejora de recetas debe ser compatible con el futuro desacople de OF, pero no incluye por sí sola seleccionar lotes, mapear consumos a áreas ni rediseñar MPS.

## 2. Evidencia de datos

### 2.1. Los cuatro graneles

Todos tienen unidad de producto `KG`. Los valores siguientes son los guardados; no deben interpretarse como una fórmula físicamente validada por kilogramo.

| Código | Nombre | `cantidadUnidad` | `rendimientoTeorico` |
|---|---|---:|---:|
| GR001 | BASE NEUTRA | 1 | 1 |
| GRTP1 | GRANEL TRATAMIENTO PREMIUM | 0,45 | 1 |
| GR002 | BASE NEUTRA BOMBONERA | 1 | 1 |
| GRSCH1 | GRANEL SACHET TRATAMIENTO | 0,72 | 0,72 |

Ingredientes y cantidades registradas, todos en kg:

| Código de insumo | Nombre | GR001 | GRTP1 | GR002 | GRSCH1 |
|---|---|---:|---:|---:|---:|
| M0101001 | AGUA | 0,980392157 | 0,5 | 3,636363 | 0,694444444 |
| MP001 | ALCOHOL CETILICO | 0,06127451 | 0,03125 | 0,2272727273 | 0,043402778 |
| MP002 | RINSOL | 0,044117647 | 0,0225 | 0,1636363636 | 0,03125 |
| MP003 | GLICERINA | 0,031862745 | 0,01625 | 0,1180818182 | 0,022569444 |
| MP008 | PROCIDE | 0,00122549 | 0,000625 | 0,004545454545 | 0,0008680555556 |

**Hecho:** cambian las cantidades de los cinco ingredientes, no solamente el agua.

**Comparación numérica:** respecto a GR001, GRTP1 contiene aproximadamente 0,51 veces cada ingrediente; GRSCH1, 0,708333333 veces; GR002, 3,7090909 veces, con una pequeña diferencia adicional de glicerina. Por ello las proporciones de los dos primeros son prácticamente iguales, salvo redondeos; GR002 no es exactamente proporcional.

En el ejemplo de bombonera, la glicerina calculada es 12,989 kg. Una escala exacta de la composición de GR001 con aproximadamente 400 kg de agua daría cerca de 13 kg. Debe confirmarse si esa diferencia es intencional.

La suma de los cinco insumos de GR001 es **1,118872549 kg**, pese a que su rendimiento guardado es 1. Esto exige confirmar la salida útil y posibles pérdidas; no demuestra por sí solo que la formulación sea incorrecta. Tampoco permite declarar GR001 como la receta canónica físicamente correcta sin validación del cliente.

### 2.2. Terminados relacionados

Se localizaron **43 terminados**, recorriendo las recetas también a través de semiterminados intermedios:

| Granel alcanzado | Cantidad | Códigos de terminados |
|---|---:|---|
| GR001 | 15 | `2111`, `21112`, `401001`, `403001`, `403002`, `403003`, `403004`, `403005`, `403006`, `403007`, `403008`, `403009`, `403010`, `403011`, `403012` |
| GRTP1 | 2 | `405002`, `405006` |
| GR002 | 16 | `1000112`, `1000113`, `1000114`, `1000115`, `404001`, `404002`, `404003`, `404004`, `404005`, `404006`, `404007`, `404008`, `404009`, `404010`, `404011`, `404012` |
| GRSCH1 | 10 | `1202503`, `202501`, `2025010`, `2025011`, `202502`, `202504`, `202506`, `202507`, `202508`, `202509` |

`401001` utiliza GR001 y pertenece a una categoría con lote de 432 unidades; no debe suponerse que todos los productos que usan GR001 tienen lote de 816.

Este documento conserva cuatro casos completos representativos. Antes de una migración deben extraerse nuevamente las recetas y órdenes afectadas: esta lista no sustituye una copia actualizada de los 43 árboles completos.

### 2.3. Casos de referencia: cadenas de consumo

Las cantidades entre productos son los coeficientes guardados, no conversiones deducidas de sus nombres comerciales.

| Terminado | Nombre | Lote de categoría | Cadena hasta el granel base |
|---|---|---:|---|
| 403004 | TRATAMIENTO CEBOLLA 24 X1000ML | 816 unidades | `403004 → 1 GRT004 → 1 GR001` |
| 405006 | TRATAMIENTO PREMIUM CEBOLLA 35 X450ML | 400 unidades | `405006 → 0,45 GTPC → 0,45 GRTP1` |
| 404003 | BOMBONERA ANGELS CEBOLLA X5 | 110 unidades | `404003 → 3,6 GRB001 → 0,2777777777777778 GR002` |
| 202507 | TRAT CEBOLLA 24 DISPLAY X 24 SOB X30GR SACHET | 288 displays | `202507 → 0,72 GRSCH003 → 0,72 GRSCH1` |

Los cuatro intermedios tienen unidad `KG`:

| Intermedio | Nombre | `cantidadUnidad` | `rendimientoTeorico` | Otros ingredientes directos |
|---|---|---:|---:|---|
| GRT004 | GRANEL TRATAMIENTO CEBOLLA | 1 | 1 | `MF016 = 0,002941176471 kg` |
| GTPC | GRANEL TRATAMIENTO PREMIUM CEBOLLA | 1 | 0,45 | `MF016 = 0,001318681 kg` |
| GRB001 | TANQUE GRANEL BOMBONERA ANGELS CEBOLLA | 3,6 | 3,6 | `MF016 = 0,0030303030303030303 kg`; `MC002 = 0,000050505050505050505 kg` |
| GRSCH003 | GRANEL SACHET TRATAMIENTO CEBOLLA | 0,72 | 0,72 | `MF016 = 0,002083333333 kg` |

`MF016` es FRAGANCIA PURE SEDUCCION y `MC002` es COLOR ROSADO.

Otros componentes directos de los terminados:

- **403004:** `SEMIT016 = 1 U` (envase termoencogido), compuesto por `ME008 = 1 U` y `ME133 = 1 U`; `SEMIT049 = 1 U` (stiker + tapa), compuesto por `ME115 = 1 U` y `ME134 = 1 U`. Empaque adicional: `ME001 = 1 U` por caja de 24.
- **405006:** `ME045 = 1 U` (etiqueta), `ME139 = 1 U` (envase), `ME140 = 1 U` (tapa rosa). Empaque adicional: `ME001 = 1 U` por caja de 35.
- **404003:** `ME071 = 1 U` (combo stiker), `ME137 = 1 U` (envase). Empaque adicional: `ME205 = 1 U` por caja de 5.
- **202507:** `ME090 = 0,04913194444 kg` (lámina), `ME157 = 1 U` (caja de sachets). Empaque adicional: `ME003 = 1 U` por caja de 24 displays.

### 2.4. Dispensación actual y sustitución por GR001

**Supuestos:** una OP nueva con el tamaño de lote de su categoría; sin cantidades manualmente editadas ni consumos previos. Se reproduce el cálculo del backend; no se ejecutaron dispensaciones ni se asignaron existencias o lotes. Una OP histórica puede tener otra cantidad.

La simulación sustituye únicamente la referencia a GRTP1, GR002 o GRSCH1 por GR001, conservando todos los coeficientes de las recetas padre.

**403004 — lote de 816 unidades, ya utiliza GR001:**

| Ingrediente | Actual, kg | Con GR001, kg |
|---|---:|---:|
| M0101001 — Agua | 800,000000 | 800,000000 |
| MP001 — Alcohol cetílico | 50,000000 | 50,000000 |
| MP002 — Rinsol | 36,000000 | 36,000000 |
| MP003 — Glicerina | 26,000000 | 26,000000 |
| MP008 — Procide | 1,000000 | 1,000000 |

**405006 — lote de 400 unidades:**

| Ingrediente | Actual con GRTP1, kg | Sustituyendo por GR001, kg |
|---|---:|---:|
| M0101001 — Agua | 40,500000 | 79,411765 |
| MP001 — Alcohol cetílico | 2,531250 | 4,963235 |
| MP002 — Rinsol | 1,822500 | 3,573529 |
| MP003 — Glicerina | 1,316250 | 2,580882 |
| MP008 — Procide | 0,050625 | 0,099265 |

**404003 — lote de 110 unidades:**

| Ingrediente | Actual con GR002, kg | Sustituyendo por GR001, kg |
|---|---:|---:|
| M0101001 — Agua | 399,999930 | 107,843137 |
| MP001 — Alcohol cetílico | 25,000000 | 6,740196 |
| MP002 — Rinsol | 18,000000 | 4,852941 |
| MP003 — Glicerina | 12,989000 | 3,504902 |
| MP008 — Procide | 0,500000 | 0,134804 |

**202507 — lote de 288 displays:**

| Ingrediente | Actual con GRSCH1, kg | Sustituyendo por GR001, kg |
|---|---:|---:|
| M0101001 — Agua | 103,680000 | 146,371765 |
| MP001 — Alcohol cetílico | 6,480000 | 9,148235 |
| MP002 — Rinsol | 4,665600 | 6,586729 |
| MP003 — Glicerina | 3,369600 | 4,757082 |
| MP008 — Procide | 0,129600 | 0,182965 |

Las cifras se redondean aquí a seis decimales. Los otros materiales permanecen iguales en ambos escenarios:

| Terminado | Materiales y cantidades por lote que no cambian |
|---|---|
| 403004 | `MF016: 2,4 kg`; `ME008, ME133, ME115 y ME134: 816 U cada uno`; `ME001: 34 U` |
| 405006 | `MF016: 0,23736258 kg`; `ME045, ME139 y ME140: 400 U cada uno`; `ME001: 11,42857143 U` |
| 404003 | `MF016: 1,2 kg`; `MC002: 0,02 kg`; `ME071 y ME137: 110 U cada uno`; `ME205: 22 U` |
| 202507 | `MF016: 0,432 kg`; `ME090: 14,15 kg`; `ME157: 288 U`; `ME003: 12 U` |

Operaciones que explican el agua:

```text
403004: 816 × 1 × 1 × 0,980392157 ≈ 800 kg
405006: 400 × 0,45 × 0,45 × 0,5 = 40,5 kg
404003: 110 × 3,6 × 0,2777777777777778 × 3,636363 ≈ 399,99993 kg
202507: 288 × 0,72 × 0,72 × 0,694444444 ≈ 103,68 kg
```

Al sustituir el código, cambia el último factor por `0,980392157`. Los demás factores se mantienen.

**Conclusión comprobada:** el reemplazo directo altera sustancialmente la dispensación. **Interpretación:** las recetas emplean escalas incompatibles con una sustitución de identidad sin ajustar cantidades. No está demostrado que las cantidades actuales sean las físicamente correctas ni que el doble factor 0,45 o 0,72 sea incorrecto por sí solo: depende de qué salida represente cada receta.

## 3. Comportamiento del software y referencias

Las rutas de backend de esta sección parten de `exotic-app-backend/src/main/java/exotic/app/planta/`. Los métodos son referencias más estables que los números de línea.

| Archivo | Responsabilidad o hallazgo |
|---|---|
| `service/productos/ProductoService.java` | `getInsumosWithStock` y `getInsumosWithStockRecursive` recuperan los coeficientes y recetas hijas sin normalizarlos por rendimiento. |
| `service/inventarios/DispensacionV2WorkflowService.java` | `buildMaterialesRequeridos`, `aplanarInsumos` y `agregarInsumosEmpaque`: multiplicación por cantidad de OP y por coeficientes de cada nivel; empaque separado por `unitsPerCase`. |
| `service/produccion/ProgramacionProduccionSemanalService.java` | La creación de ítems y lotes planificados obtiene `loteSize` de la categoría y lo usa como cantidad planificada de cada lote. |
| `service/produccion/MaterialRequirementSnapshotService.java` | `expandirDispensables` y `expandirOrdenes` multiplican cantidades al construir requerimientos congelados y demandas de OF; tampoco normalizan por rendimiento. |
| `service/produccion/AreaOperativaPanelDetalleService.java` | `buildBomRecetaNode` calcula cantidades del árbol de insumos con multiplicadores. Es otra vista que debe mantenerse coherente. |
| `service/productos/ProductoManufacturingService.java` | `buildInsumo` guarda el coeficiente recibido; el proceso guarda el rendimiento por separado. `saveManufacturingSnapshot` conserva los datos de manufactura en JSON. |
| `service/productos/ProductoCostoPropagacionService.java` | `construirPlan` suma `costoInput × cantidadRequerida` sin dividir por una salida de receta. Cambiar la base de cantidades también exige revisar el costo por unidad. |
| `service/productos/templates/CategoriaManufacturingTemplateService.java` | Las plantillas conservan rendimiento e insumos; sus subtotales también dependen de cantidades. Deben adoptar la misma semántica. |

**Datos frente a comportamiento:** al consultar producción el 14 de octubre, `BATCH_RECORD_WORKFLOW_ENABLED` estaba en `false` y los cuatro graneles tenían `requiereOrdenFabricacion = false`. El cálculo analizado expandía las recetas vigentes. El backend desplegado entonces correspondía al commit `33ce83a8694164bb58d164329b9731c0c0a28fff`; se comprobó la coincidencia de los archivos relevantes con ese commit. No se afirma que ese sea el despliegue actual del 20 de octubre.

En el frontend, las rutas siguientes parten de `exotic-app-frontend/src/pages/Productos/`:

| Archivo | Hallazgo o función relevante |
|---|---|
| `manufacturingMapper.ts` | Transporta cantidades de insumos y rendimiento como campos separados; no normaliza los insumos. |
| `DefSemiTer/consulta/DetalleProductoSemiTer.tsx` | Indica que las cantidades corresponden a una unidad del producto. Esa interpretación debe concordar con el formulario y el cálculo. |
| `DefSemiTer/CodificarSemioTermiTab/StepThree/SemiterminadosStep2DefineProcess.tsx` | Permite introducir el rendimiento teórico como número. |
| `DefSemiTer/consulta/ModSemioTerMFversions/StepThree/StepThree_ModProdMF.tsx` | Edición equivalente del rendimiento. |
| `DefProcesses/CreadorProcesos/ProcessDesigner.tsx` | Coordina el diagrama de fabricación del producto. |
| `DefProcesses/CreadorProcesos/Nodos/TargetNode.tsx` | Muestra nombre/tipo del producto de salida; actualmente no presenta una cantidad de salida explícita. |

Por tanto, **`rendimientoTeorico` y `cantidadUnidad` no participan en el cálculo de dispensación estudiado**. Esto no equivale a afirmar que los campos no se guarden, exporten o muestren en ninguna otra funcionalidad.

### 3.1. Observaciones adicionales para no perder

- `Producto.tipoUnidades` indica la unidad del producto. `cantidadUnidad` tiene como descripción contenido por envase/empaque, pero carece de una unidad de contenido propia. Un producto con unidad `U` y contenido `0,45` no expresa por sí mismo si son kg o litros.
- `405002`, premium romero de 450 ml, tiene `cantidadUnidad = 0,45` y rendimiento `0,45`; `405006`, premium cebolla de 450 ml, tiene ambos valores en `1`. Confirma que esos campos necesitan revisión de significado y datos.
- El agua `M0101001` no es inventariable, pero tiene `consumoDirecto = true`; debe seguir figurando en la dispensación.
- `DispensacionV2WorkflowService.addMaterial` descarta aportes `<= 0,01` antes de acumularlos. En `404010` eso omite `MC006` y `MC007`, de 0,01 kg cada uno. Es un hallazgo independiente de la sustitución de granel.
- El empaque adicional usa `cantidadOrden / unitsPerCase × cantidadEmpaque`, sin redondear a cajas enteras. De ahí los 11,42857143 corrugados del ejemplo premium. La política de redondeo debe decidirse separadamente.
- Los cálculos operativos usan `double`, mientras que los snapshots emplean `BigDecimal` con escala 6 en pasos intermedios. La nueva regla debe definir precisión y redondeo coherentes.

Estas observaciones no autorizan cambios colaterales automáticos. Deben incorporarse al alcance que el usuario apruebe.

## 4. Modelo conceptual propuesto

### 4.1. Separar significados

| Concepto | Definición propuesta | Ejemplo |
|---|---|---|
| Unidad del producto | Unidad en que se solicita, consume y lleva stock del producto. | Granel: kg; terminado: U. |
| Salida teórica de receta | Cantidad esperada de producto obtenida con todos los insumos registrados. No es un porcentaje. | 800 kg de GR001. |
| Cantidad de insumo | Cantidad de un ingrediente necesaria para esa salida de receta, en la unidad del ingrediente. | X kg de agua para 800 kg de salida. |
| Cantidad a fabricar | Demanda concreta de la OP/OF, en la unidad del producto. | 200 kg de GR001 o 400 frascos. |
| Tamaño de lote planificado | Cantidad por orden/lote empleada al programar producción. No redefine la receta. | 400 frascos por OP. |
| Contenido por envase | Contenido comercial de una unidad terminada, con su unidad explícita. | 450 ml/U. |
| Unidades por caja | Agrupación logística y base del empaque adicional. | 35 frascos/caja. |

Para sachets debe decidirse expresamente si `U` significa sobre o display. En los ejemplos analizados corresponde al display según nombre y receta. No introducir otro nivel de presentación sin un requerimiento concreto.

### 4.2. Regla de proporcionalidad

```text
factor = cantidad solicitada del producto / salida teórica de su receta
cantidad de cada ingrediente = cantidad registrada del ingrediente × factor
```

Ambas cantidades del cociente deben estar en la misma unidad. Al expandir un semiterminado, la cantidad requerida de ese semiterminado es la demanda de su propia receta y se divide por **su propia salida**, una sola vez.

Ejemplo ilustrativo, no transcripción de la receta de producción:

- Receta A: 80 kg de ingrediente para obtener 800 kg de granel.
- Receta B equivalente: 0,1 kg de ingrediente para obtener 1 kg de granel.
- Demanda de 200 kg: ambas deben solicitar 20 kg del ingrediente.

Para un terminado con receta para 100 U, todos sus ingredientes de receta, incluidos envases y etiquetas, corresponden a esas 100 U. El empaque adicional de `CasePack` sigue calculándose por caja; no debe dividirse otra vez por la salida de receta.

El contenido por envase puede ayudar a validar, pero no debe convertirse en otro multiplicador implícito. La cantidad de granel consumida se declara en la receta. **450 ml no equivalen automáticamente a 0,45 kg**; una conversión masa/volumen requeriría densidad o un coeficiente explícito validado. No hace falta añadir un sistema general de conversiones en esta primera mejora.

## 5. Entidades: opciones de cambio mínimo

La decisión final sigue pendiente. La posibilidad de una entidad adicional no implica que sea necesaria.

| Opción | Cambio | Ventaja | Condición o coste |
|---|---|---|---|
| A. Ampliar lo existente | Dar a `ProcesoProduccionCompleto.rendimientoTeorico` el significado explícito de salida de receta; añadir identificación de la semántica de cálculo y unidad de contenido al producto. | Menor cambio estructural. | La base de la receta seguiría alojada en el modelo del proceso. Debe estar disponible para todas las recetas, sus versiones y plantillas. |
| B. Una entidad `BaseReceta` | Asociar a cada S/T una cabecera con salida teórica y semántica de cálculo. Mantener las listas actuales de `Insumo` y los diagramas. | Separa la definición cuantitativa de receta del diagrama. | Nueva relación y migración; debe evitarse que el rendimiento del proceso y la cabecera sean dos fuentes editables del mismo dato. |

**Orientación:** priorizar A si la dependencia receta/proceso resulta adecuada en los flujos existentes. Elegir B si se acuerda que la receta necesita una identidad cuantitativa independiente del diseñador. No se justifica crear otro árbol de ingredientes ni otra jerarquía Material/SemiTerminado/Terminado.

Campos candidatos, todavía sin fijar nombres ni ubicación definitiva:

| Campo o cambio | Propósito |
|---|---|
| Salida teórica positiva | Cantidad de producto obtenida por la receta. Reutilizar `rendimientoTeorico` o trasladar su responsabilidad a `BaseReceta`, según la opción elegida. |
| Semántica de cálculo | Distinguir explícitamente recetas anteriores de recetas normalizadas por salida, sin inferirlo por fecha, código o valor numérico del rendimiento. Debe quedar versionada. |
| `unidadContenido` en `Producto` | Acompañar `cantidadUnidad` cuando represente contenido comercial. |
| Unidad de salida en snapshots/contratos | Conservar el significado histórico. En el modelo vivo puede derivarse de `Producto.tipoUnidades` para evitar dos unidades independientes contradictorias. |

No es obligatorio añadir una unidad editable a cada `Insumo`: inicialmente puede exigirse la unidad del producto ingrediente. Las conversiones de captura a esa unidad pueden analizarse después.

### 5.1. Entidades existentes involucradas

Inventario inicial: **11 entidades del dominio de productos y 3 entidades operativas relacionadas**. Participar en el análisis no significa que todas requieran cambios persistentes.

Rutas desde `exotic-app-backend/src/main/java/exotic/app/planta/model/`:

| Entidad | Archivo | Papel |
|---|---|---|
| Producto | `producto/Producto.java` | Unidad, contenido y costo. |
| Material | `producto/Material.java` | Ingrediente final, stock o consumo directo. |
| SemiTerminado | `producto/SemiTerminado.java` | Receta y modalidad integrada/con OF. |
| Terminado | `producto/Terminado.java` | Receta, categoría y empaque. |
| Insumo | `producto/manufacturing/receta/Insumo.java` | Relación ingrediente/cantidad. |
| ProcesoProduccionCompleto | `producto/manufacturing/procesos/ProcesoProduccionCompleto.java` | Rendimiento guardado y diagrama. |
| ManufacturingVersions | `producto/manufacturing/snapshots/ManufacturingVersions.java` | JSON históricos de receta, proceso y empaque. |
| CasePack | `producto/manufacturing/packaging/CasePack.java` | Unidades por caja. |
| InsumoEmpaque | `producto/manufacturing/packaging/InsumoEmpaque.java` | Consumo adicional por caja. |
| Categoria | `producto/Categoria.java` | Tamaño de lote de planificación. |
| CategoriaManufacturingTemplate | `producto/manufacturing/templates/CategoriaManufacturingTemplate.java` | Creación de productos con insumos y proceso predefinidos. |
| OrdenProduccion | `produccion/OrdenProduccion.java` | Cantidad concreta del terminado. |
| OrdenFabricacion | `produccion/fabricacion/OrdenFabricacion.java` | Cantidad concreta del semiterminado. |
| BatchRecord | `produccion/batchrecord/BatchRecord.java` | Requerimientos congelados y trazabilidad. |

El inventario de subentidades de plantillas, DTO, repositorios y migraciones se cerrará al elegir A o B. Nuevas entidades propuestas: **0 con A; 1 con B**.

## 6. Modelo de archivos e impacto entre módulos

La sección 3 identifica **8 servicios backend y 6 archivos frontend** que explican directamente el comportamiento. Sumados a los **14 archivos de entidades** anteriores son **28 archivos de referencia principal**, no una lista de archivos autorizados a modificar.

Además, el inventario de implementación debe cubrir:

| Área | Archivos o puntos de entrada adicionales | Qué preservar o adaptar |
|---|---|---|
| Contratos Productos | `src/pages/Productos/types.tsx`; DTO en `model/producto/dto/manufacturing/`, incluido `ProductoManufacturingDTO.java` | Semántica, salida y unidad de contenido coherentes entre frontend y backend. |
| Alta y modificación | `DefSemiTer/CodificarSemioTermiTab/StepOne/`, `StepTwo/`, `StepFour/`; `DefSemiTer/consulta/ModSemioTerMFversions/StepTwo/` y `StepFour/` | Formularios, cantidades, confirmación y validación final. |
| Plantillas | `DefSemiTer/Templates/CategoriaManufacturingTemplateDesigner.tsx`; `DefSemiTer/CrearDesdePlantilla/CrearDesdePlantillaTab.tsx` | No crear productos con una base distinta de la que el usuario ve. |
| Empaque | Ambos `StepThree/PackagingTerminadoDefiner.tsx` de alta y modificación | Conservar la distinción entre receta de producto y material por caja. |
| OF | `service/produccion/OrdenFabricacionService.java`; `OrdenFabricacionAutoGenerationService.java` | Coherencia entre demanda del semiterminado, fabricación y consumo desde stock. |
| Almacén | `src/pages/TransaccionesAlmacen/AsistenteDispensacion/DispensacionV2Service.ts` y `DispensacionV2Step3Materiales.tsx` | Cantidades sugeridas, edición autorizada y presentación de unidades. |
| Exportación/importación | `service/commons/ExportacionTerminadoService.java` y los flujos de carga/restauración aplicables | Conservar semántica y base de receta; tratar explícitamente archivos antiguos sin esos campos. |
| Costos | `ProductoCostoPropagacionService`, subtotales en `ProductoManufacturingService` y plantillas | Diferenciar costo de la receta completa y costo por unidad de salida; revisar invalidación de planes cuando cambie la base. |
| E2E y contratos | Repositorio `exotic-app-e2e` | Actualizar pruebas de contratos y casos funcionales cuando se apruebe la implementación. |

Antes de implementar, convertir este mapa en una lista cerrada de archivos nuevos/modificados y contarlos por módulo. No prometer que basta con modificar únicamente el formulario y la dispensación.

La regla matemática debe ser idéntica en dispensación, demandas OF, costos y vistas. Si se extrae una función común de backend, delimitarla a la normalización cuantitativa y revisar todos sus consumidores. No centralizar componentes de interfaz por mera semejanza.

### 6.1. Gaphor

Existe el diagrama **«Productos — componente en crudo»** en `exotic-app-architecture/ExoticApp.gaphor`. El artefacto documental `temp.md` pertenece al paquete Productos que contiene ese diagrama y referencia `Productos/temp.md`, relativo al archivo del modelo. No pertenece al paquete interno que reproduce los archivos del frontend.

La referencia documental está incorporada al árbol del modelo. No se modifican las figuras del diagrama, los artefactos de código ni sus relaciones. Cuando se elija una opción de entidades, deberán reflejarse manualmente la responsabilidad de la salida de receta y las dependencias efectivamente modificadas. No se declara aprobado ni sincronizado un diseño futuro.

## 7. Layout de interfaz propuesto

Conservar los asistentes y el diseñador actuales:

1. **Datos del producto:** unidad del producto; contenido por envase y su unidad cuando aplique. Mostrar ambos conceptos con etiquetas distintas.
2. **Insumos:** cabecera visible «Estas cantidades producen: [800] [kg] de GR001». Cada fila expresa la cantidad en la unidad del ingrediente.
3. **Diseñador:** el nodo de salida muestra el mismo valor: «GR001 · salida de receta: 800 kg». Es una proyección del dato, no otra fuente editable independiente.
4. **Confirmación/consulta:** mostrar base de receta, cantidades registradas y vista normalizada por unidad.
5. **Simulación:** introducir una cantidad a fabricar y previsualizar insumos requeridos sin guardar cambios. Mantener el alcance inicial pequeño; puede ser una sección del formulario.

Cambiar solo la salida manteniendo los ingredientes **cambia la proporción de la receta**. Reexpresar una receta equivalente de 1 kg a 800 kg implica multiplicar también sus insumos por 800. La interfaz debe distinguir ambas intenciones; no reescalar silenciosamente.

No trasladar al usuario nombres de modos internos de compatibilidad. La interfaz debe explicar qué representan las cantidades y señalar recetas pendientes de revisión.

## 8. Transición y protección del funcionamiento existente

1. **Fijar la semántica antes de migrar.** Los valores históricos de rendimiento no se usaban como divisor y no pueden activarse globalmente sin revisión.
2. **Separar compatibilidad matemática de corrección de formulaciones.** Se puede conservar el resultado actual tratando los coeficientes anteriores como cantidades por unidad efectiva. Eso no certifica que la fórmula física sea correcta.
3. **Identificar la semántica por versión.** Una versión antigua conserva su interpretación. Una versión nueva normalizada guarda salida y unidades suficientes para reproducir el cálculo.
4. **No confiar solamente en crear una versión nueva.** El flujo sin batch record consulta recetas vivas: cambiar un semiterminado puede afectar OP abiertas. Antes de migrar, decidir cómo congelar/preservar sus requerimientos o impedir el cambio mientras existan órdenes afectadas.
5. **Preservar snapshots existentes.** No recalcular ni sobrescribir cantidades de batch records, consumos o costos históricos como efecto secundario de la mejora.
6. **Mantener coherente toda la cadena.** Si padre e hijo usan semánticas diferentes durante la transición, cada receta debe interpretar su propia base explícitamente. No aplicar una división global al árbol.
7. **Mantener la modalidad OF/integrada.** Un semiterminado con OF se requiere como producto con stock/lote; su OF calcula sus ingredientes. No dispensar simultáneamente el granel y sus materias primas para el mismo consumo.
8. **Probar primero en staging con autorización.** Ningún cambio productivo ni sustitución de códigos está autorizado por este documento.
9. **Consolidar después de validar.** Sustituir referencias futuras a los duplicados por GR001 únicamente tras aprobar proporciones y cantidades. Conservar los códigos y referencias necesarios para historia, stock y trazabilidad.

Si se modifica la base de una receta, revisar también invalidaciones de cálculos de costos, versiones utilizadas por las órdenes y los datos conservados por exportaciones. Un cambio de etiqueta del campo no resuelve esas dependencias.

## 9. Decisiones que todavía requieren definición

| Decisión | Información necesaria |
|---|---|
| Fórmula física de referencia | Cantidades aprobadas y salida útil real de GR001; pérdidas incluidas y unidad de salida. |
| Diferencia de glicerina | Confirmar si GR002 debe conservarla o si es un error de datos. |
| Ubicación de la base | Elegir ampliación de `ProcesoProduccionCompleto` o entidad `BaseReceta`. |
| Semántica del contenido | En qué productos aplica `cantidadUnidad`, con qué unidad y cómo describir displays/paquetes. |
| Recetas pendientes y órdenes abiertas | Cómo preservar cálculos en el flujo que usa recetas vivas y cuándo permitir la transición. |
| Reexpresión de una receta | Si se ofrece una acción explícita para reescalar todos los ingredientes o solo una simulación. |
| Precisión | Decimales de cálculo/presentación, tolerancias por unidad y tratamiento de consumos pequeños. |
| Empaque | Mantener o cambiar la política actual de cajas fraccionarias, como alcance separado y explícito. |
| Costos | Confirmar el significado de costo unitario y el tratamiento del empaque adicional al normalizar recetas. |

Estas decisiones no se pueden completar únicamente mediante inspección del código. En particular, los datos existentes no permiten deducir automáticamente el rendimiento físico correcto.

## 10. Criterios de aceptación para la futura mejora

- Una receta expresada para 1 kg y otra proporcionalmente equivalente para 800 kg generan la misma dispensación para una misma demanda.
- El escalado se aplica correctamente en cadenas de varios semiterminados y al acumular un ingrediente que aparece en varias ramas.
- Se puede reutilizar GR001 en distintas presentaciones sin alterar su composición para compensar el tamaño del envase.
- La receta de un terminado se escala por unidades de terminado; su contenido comercial no se multiplica de nuevo implícitamente.
- Crear, editar, consultar, crear desde plantilla, exportar e importar conserva el mismo significado de las cantidades.
- La vista de área operativa, la dispensación, los requerimientos del batch record y la demanda OF muestran cantidades coherentes.
- El costo unitario conserva su significado aunque la receta se registre para 1 o para 800 unidades de salida.
- Los modos integrado y con OF evitan el doble consumo. El consumo directo de agua sigue funcionando.
- Salida cero/negativa, cantidades inválidas, referencias cíclicas y unidades incompatibles se detectan sin realizar operaciones parciales.
- Se valida el comportamiento con cantidades pequeñas como los 0,01 kg de colorantes, sin confundir tolerancia de comparación con eliminación de ingredientes.
- La política de empaque queda explícita y no cambia accidentalmente.
- Las recetas y órdenes anteriores conservan sus resultados durante la transición; los snapshots históricos permanecen intactos.
- Los cuatro ejemplos de este documento sirven como casos de regresión del comportamiento anterior y como comparativa contra las formulaciones futuras aprobadas.

## 11. Alcance de la evidencia

Los datos de octubre 14 y la reproducción matemática permiten explicar con alta confianza por qué cambiar solo el código del granel cambia las cantidades. La revisión estática adicional de octubre 20 identifica impactos en costos, plantillas, áreas y snapshots.

No se certificó la fórmula física de fabricación, no se ejecutaron pruebas funcionales remotas y no se modificaron datos. Los CSV temporales de la investigación original no están disponibles en este equipo al preparar el documento; por eso se conservaron aquí las cantidades y cadenas de los casos representativos, sin depender de enlaces a `/tmp`.

El siguiente paso es resolver las decisiones de la sección 9 y cerrar **entidades → archivos → interfaz**. La implementación posterior deberá materializar ese alcance aprobado, sin convertir esta mejora en una reestructuración general del módulo.
