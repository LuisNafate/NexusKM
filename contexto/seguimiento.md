# Plan y seguimiento

**Actualización** 18 de noviembre de 2026.  
**Entrega anunciada** 27 de noviembre de 2026. Hora y medio de envío pendientes de confirmar.

## Trabajo completado en esta carpeta

Se copiaron los 33 archivos de NexusKM y el ZIP del usuario. Los archivos de la carpeta, los del ZIP y las copias del proyecto coinciden mediante SHA-256. Se revisaron los scripts Cypher, el documento académico, el texto de las 19 diapositivas y el chat compartido. El inventario está en [migracion.json](migracion.json).

Se actualizó la propuesta del dominio y se redactaron una arquitectura inicial para los tres modelos y una revisión adversaria. Las pruebas del servidor corresponden al reporte histórico del 12 de noviembre. La validación técnica de esta migración comprende los archivos y el análisis estático.

## Cobertura de los ocho entregables

| Entregable | Material disponible | Trabajo pendiente |
| --- | --- | --- |
| 1. Propuesta | Dominio, usuarios, doce RF y nueve consultas del trabajo anterior. [Ficha](tema.md) completada. | Validar alcance de la entrega integrada y justificar cada modelo con sus operaciones. |
| 2. Modelado | Diccionario, relaciones, reglas y diagramas del grafo. | Completar modelos relacional y documental. Resolver las diferencias del grafo y el mínimo de propiedades de Rol. |
| 3. Arquitectura | [Asignación propuesta](arquitectura_propuesta.md) y flujos de gobernanza previos. | Elegir tecnologías, comparar alternativas y cerrar propiedad de datos, sincronización y contratos. |
| 4. Tres bases | Diez scripts Cypher y resultados históricos de Neo4j. | Esquemas y carga relacional y documental. Validación actual del grafo y correcciones derivadas de la revisión. |
| 5. Catálogo | Consultas Q1–Q9 y resultados resumidos de varias consultas. | Añadir parámetros, validaciones, casos límite y negativos, operaciones de las otras bases y flujos combinados. Corregir Q2. |
| 6. Backend y API | Material de diseño del dominio. | Implementar API, servicios, repositorios, validación, autorización, errores y configuración. |
| 7. Aplicación | Ejemplos ficticios para demostrar el dominio. | Implementar interfaz y flujos de consulta, modificación y eliminación o baja. Verificar integración. |
| 8. Pruebas y ejecución | T1–T10 para el grafo y resumen histórico. | Casos adversarios, pruebas por base y de extremo a extremo, fallos parciales, concurrencia y rendimiento según alcance. Manual reproducible y evidencia actual. |

## Próximo hito

Cerrar la matriz de responsabilidades y los modelos relacional y documental usando los identificadores existentes. La [propuesta de arquitectura](arquitectura_propuesta.md) ofrece el primer borrador. En paralelo al diseño, resolver el propietario aprobador de SOL-001, el criterio de vigencia de Q2 y el alcance de las cardinalidades.

## Fechas internas propuestas

| Noviembre | Resultado esperado |
| --- | --- |
| 18–19 | Alcance definido, modelos compatibles, responsabilidad por dato y revisión del grafo. |
| 20–22 | Esquemas y carga de las tres bases, consultas y contrato de API. |
| 23–24 | Backend e interfaz con un flujo integrado demostrable. |
| 25–26 | Pruebas, fallos parciales, ejecución desde cero y actualización de documentos y presentación. |
| 27 | Repositorio, documentación y evidencias listos para el envío. |

## Decisiones y pendientes

| Fecha | Tema | Estado o decisión |
| --- | --- | --- |
| 16 de noviembre | Contexto académico | Guía, anuncio, material de grafos y requisitos organizados. |
| 18 de noviembre | Tema y migración | NexusKM elegido por el usuario. Copia verificada del paquete y síntesis del chat. |
| 18 de noviembre | Arquitectura integrada | Borrador propuesto, pendiente de evaluación con el equipo. |
| Por registrar | Integrantes y disponibilidad | Pendiente. |
| Por definir | Motores relacional y documental, lenguaje, API e interfaz | Pendiente del diseño y comparación tecnológica. |
| Por comprobar | Estado de la instancia nexuskm | Evidencia histórica disponible. La migración verifica archivos. |
| Por confirmar | Hora, canal de entrega y rúbrica adicional | Pendiente de información del profesor. |

Al cerrar una decisión, registra su motivo y actualiza los documentos afectados. Para cerrar un entregable, enlaza sus artefactos y la evidencia de su ejecución.
