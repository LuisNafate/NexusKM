# Revisión adversaria de NexusKM

**Fecha** 18 de noviembre de 2026.  
**Método** Contraste estático entre requisitos, scripts, diccionario, diagramas, presentación y evidencia recibida. Los contraejemplos de esta revisión describen escenarios por ejecutar en un entorno de prueba.

## Base de la revisión

El paquete y su ZIP coinciden en los 33 archivos. Incluyen diez scripts Cypher, siete diagramas, documento académico de 16 páginas, presentación de 19 diapositivas y tres imágenes de evidencia. El reporte histórico declara 63 nodos, 87 relaciones, 23 etiquetas, 33 tipos de relación y 24 restricciones.

Se revisaron las sentencias del esquema y los datos de ejemplo. El archivo 01 contiene 24 declaraciones de unicidad y 6 índices explícitos. Se identificaron 33 nombres de tipos de relación en los scripts. Estos recuentos de archivos son compatibles con parte del reporte histórico. El número actual de nodos, relaciones e índices del servidor requiere una consulta a la instancia.

## Hallazgos comprobados en los archivos

| ID | Prioridad | Observación y referencia | Acción para resolverla |
| --- | --- | --- | --- |
| A01 | Alta | DOC-003 tiene como propietario a PER-002, Carlos Ruiz, en [04_relationships_core.cypher](../NexusKM/cypher/04_relationships_core.cypher). APR-004, de tipo PROPIETARIO para SOL-001 sobre VER-003 de DOC-003, fue emitida por PER-005, Sofía Herrera, en [06_governance.cypher](../NexusKM/cypher/06_governance.cypher). La delegación existente es de PER-002 a PER-004. T1–T9 carecen de una comprobación del propietario aprobador. | Resolver quién debe aprobar y cómo se acredita una delegación válida. Después, alinear datos, validación de escritura, prueba y narrativa de publicación. |
| A02 | Alta | Q2 anuncia documentos vigentes en [08_queries.cypher](../NexusKM/cypher/08_queries.cypher), pero su patrón devuelve todas las versiones enlazadas. VER-003 figura como BORRADOR y tiene vencimiento del 14 de noviembre en [02_nodes_core.cypher](../NexusKM/cypher/02_nodes_core.cypher). | Definir vigencia con estado documental, estado de versión y fechas aplicables. Añadir el filtro y probar borrador, versión vencida y fecha ausente. |
| A03 | Media | Rol tiene únicamente rolId y nombre tanto en la carga como en el diccionario. La actividad del profesor pide al menos tres propiedades por entidad. | Definir una tercera propiedad pertinente y documentar obligatoriedad y unicidad de cada campo. Revisar las demás entidades con el mismo criterio. |
| A04 | Media | El [modelo lógico resumido](../NexusKM/diagramas/07_modelo_logico.mmd) restringe DESDE a Microservicio. En [05_dependencies.cypher](../NexusKM/cypher/05_dependencies.cypher), DEPTEC-003 parte de Documento DOC-001 hacia API-001. | Ampliar el diagrama para representar los tipos de origen admitidos y sus reglas. Completar mínimos y máximos de los tipos de relación del catálogo. |
| A05 | Alta | T5 cuenta personas distintas conectadas a aprobaciones técnicas. Las pruebas de [09_tests.cypher](../NexusKM/cypher/09_tests.cypher) omiten la cardinalidad individual de EMITIDA_POR y APRUEBA_SOLICITUD, así como la habilitación del rol del revisor. | Validar una solicitud y un emisor por aprobación, además de identidad, actividad y facultad para aprobar. |
| A06 | Alta | [01_constraints.cypher](../NexusKM/cypher/01_constraints.cypher) declara unicidad. Los campos obligatorios, dominios de valores y cardinalidades del diccionario requieren validaciones adicionales en la capa de escritura o restricciones compatibles con el motor. | Definir dónde se hace cumplir cada regla y comprobar casos inválidos. La unicidad se aplica sobre los valores presentes y la existencia es un tipo de restricción distinto. [Manual de restricciones](https://neo4j.com/docs/cypher-manual/current/schema/constraints/create-constraints/). |
| A07 | Alta | T8 revisa únicamente horasHabilesAprobadas mayores de 48 o ausentes en excepciones CRITICA. Los valores negativos, la criticidad ALTA y la relación entre inicio y fechaLimite quedan fuera. Q5 calcula vencimiento antes de revisar si una excepción ya está cerrada. | Validar rango positivo, reglas por criticidad, fechas y estados terminales. Probar cierre, falta de fecha y límites temporales. Documentar el calendario laboral utilizado. |
| A08 | Alta | Los scripts usan SET para escribir valores de muestra al reencontrar identificadores. En 05, el patrón MERGE de DEPENDE_DE incluye criticidad y dependenciaId. Una modificación de esas propiedades puede alterar el resultado de la reejecución y crear un patrón adicional. | Definir el uso de la carga como conjunto ficticio y gestionar cambios de relaciones por identidad estable. Registrar divergencias antes de aplicar nuevamente datos de muestra sobre un entorno con cambios. MERGE busca el patrón descrito y SET actualiza las propiedades indicadas. [Manual de MERGE](https://neo4j.com/docs/cypher-manual/current/clauses/merge/). |
| A09 | Media | [07_security_sync_audit.cypher](../NexusKM/cypher/07_security_sync_audit.cypher) conserva al actor humano mediante una relación opcional. El valor SISTEMA del ejemplo termina sin propiedad de actor explícita. Q6 etiqueta como SISTEMA a cualquier evento cuyo actor no se resuelva. | Registrar tipo e identificador de actor y distinguir el proceso del sistema de una referencia humana ausente. Definir protección del historial. |
| A10 | Alta | Las consultas de violación T1–T9 pueden devolver cero filas sobre una base vacía. T10 muestra conteos y carece de aserciones de datos esperados. Un MATCH sin registros puede dejar una carga incompleta sin generar error de ejecución. | Comprobar precondiciones, cobertura de etiquetas e identificadores y resultados esperados, además de ausencia de violaciones. |
| A11 | Alta | El material previo se centra en Neo4j y deja interfaz y capa de aplicación fuera del MVP. La [guía final](fuentes/Guia_Proyecto_Final_Bases_Datos.pdf) pide los tres modelos, API, interfaz, integración y ejecución reproducible. | Implementar la ampliación del alcance con responsabilidades explícitas y completar la matriz de entregables del seguimiento. |
| A12 | Media | La presentación y los diagramas describen publicación, escalamiento y auditoría como flujos. La carga inserta eventos y estados de ejemplo. SOL-001 figura APROBADA mientras VER-003 conserva BORRADOR y DOC-003 EN_REVISION. | Especificar la transición entre aprobación y publicación. Indicar qué parte del flujo se demuestra con datos y qué parte ejecutará el backend. |
| A13 | Media | [02_resultados_consultas.md](../NexusKM/evidencias/02_resultados_consultas.md) resume varias consultas y omite Q2 y el conjunto completo de resultados. Las imágenes son reconstrucciones declaradas. El paquete contiene un reporte histórico de pruebas y carece de un registro bruto por sentencia. | Obtener una ejecución fechada con resultados completos, entorno, parámetros y salidas comprobables. Documentar las visualizaciones como reconstrucciones. |

## Contraejemplos para la siguiente validación

Estos casos derivan de la lectura de las sentencias. Su resultado observado se registrará al ejecutarlos en una base de prueba.

| Caso | Cambio adversario | Comprobación esperada |
| --- | --- | --- |
| C01 | Una persona ajena al propietario emite una aprobación PROPIETARIO. | La operación rechaza la aprobación o exige una delegación aplicable y vigente. |
| C02 | Una aprobación técnica se enlaza a dos personas o dos solicitudes. | Una validación detecta la cardinalidad inválida aunque el conteo global de revisores llegue a dos. |
| C03 | Una persona activa sin rol técnico intenta aprobar técnicamente. | El servicio verifica la facultad del revisor y rechaza el comando. |
| C04 | Consultar Q2 con un borrador, una versión vencida y una versión vigente. | La definición adoptada de vigencia determina cuáles se devuelven. |
| C05 | Excepción crítica con -1 horas, alta con 73 horas o fechaLimite anterior al inicio. | Las validaciones detectan rango, criticidad y orden temporal inválidos. |
| C06 | Excepción CERRADA con fecha límite pasada o VIGENTE sin fecha límite. | El estado terminal se conserva y la fecha faltante se reporta conforme a la política. |
| C07 | Ejecutar las pruebas sobre una base vacía o con una fase de carga omitida. | Las comprobaciones de precondiciones y cobertura fallan. |
| C08 | Cambiar la criticidad de una dependencia y repetir la carga. | Se identifica y reconcilia la diferencia entre el registro y las relaciones derivadas. |
| C09 | Dos comandos simultáneos cambian el líder o el estado de una solicitud. | La operación conserva la regla del dominio y comunica el conflicto concurrente. |
| C10 | La actualización relacional termina y falla la proyección documental o de grafo. | Se conserva el estado real de cada paso y un mecanismo recuperable de reintento o reconciliación. |
| C11 | Repetir el mismo comando después de un tiempo de espera sin respuesta. | La identificación de la operación permite evitar efectos duplicados. |
| C12 | Una persona sin autorización intenta leer un documento RESTRINGIDO mediante la API. | La respuesta respeta la autorización y queda evidencia del rechazo según alcance. |
| C13 | Dar de baja un documento o activo con dependencias e historial. | La operación aplica la política definida y conserva referencias consistentes en las tres bases. |

## Orden de resolución propuesto

Primero cerrar la propiedad del dato, la autoridad del aprobador y los estados de publicación. A continuación, completar los modelos de las tres bases y corregir la consulta de vigencia, el diccionario y el diagrama. Después implementar las operaciones con sus validaciones y probar los casos de fallo antes de actualizar la evidencia y la presentación de entrega.

El patrón de estados, las referencias y las fechas necesitan validación explícita. En Cypher, una propiedad ausente produce null y las comparaciones con null requieren tratamiento específico en filtros. [Manual sobre null](https://neo4j.com/docs/cypher-manual/current/values-and-types/working-with-null/).
