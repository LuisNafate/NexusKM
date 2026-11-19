# NexusKM

Proyecto académico de gestión de conocimiento técnico para una empresa de software, modelado como grafo en Neo4j.

## Entregables

- `documentacion/NexusKM_documento_academico_actualizado.docx`: documento formal editable con evidencia de ejecución.
- `documentacion/NexusKM_documento_academico_actualizado.pdf`: versión PDF para entrega.
- `presentacion/NexusKM_presentacion_clase_final_actualizada.pptx`: presentación editable basada en la ejecución real del MVP.
- `cypher/`: scripts ordenados, idempotentes y comentados para Neo4j Desktop 2.
- `diagramas/`: flujos editables en Mermaid.
- `prompt_codex/`: prompt de traspaso y guía para conectar Codex a Neo4j mediante MCP.

## Estado de los requisitos

- **Confirmado en el levantamiento simulado:** Neo4j Desktop 2, base `nexuskm`, datos ficticios, un departamento base por persona, un departamento propietario y un líder por proyecto, dependencias técnicas, conocimiento documental, doble aprobación técnica, excepciones temporales, seguridad, sincronización y auditoría.
- **Propuesta de diseño del equipo:** nodos explícitos para aprobaciones, solicitudes, excepciones, delegaciones, conflictos, sincronizaciones y eventos; plazos de 48 horas hábiles para criticidad crítica y 72 para alta; clasificación de documentos y validaciones de cardinalidad.
- **Fuera del MVP:** interfaz web, SSO, correo/notificaciones reales, cálculo automático de horas hábiles, conectores productivos, cifrado administrado por la aplicación, control de acceso fino dentro de Neo4j Community y automatización de respaldos.

## Ejecución en Neo4j Desktop 2

1. Inicia la instancia y abre **Query**.
2. Selecciona la base `nexuskm`. Si tu edición no permite bases múltiples, usa `neo4j` y conserva el mismo orden de scripts.
3. Ejecuta `00_preflight.cypher` y revisa versión, edición y base activa.
4. Ejecuta, en orden, `01_constraints.cypher` a `07_security_sync_audit.cypher`.
5. Ejecuta `08_queries.cypher` para la demostración.
6. Ejecuta `09_tests.cypher`. Las consultas marcadas como pruebas de violación deben devolver cero filas.

Neo4j Query puede requerir ejecutar cada sentencia por separado. Todos los datos son ficticios. Los scripts usan `MERGE` e identificadores únicos para permitir reejecución sin duplicar el conjunto de prueba.

## Orden de scripts

| Orden | Archivo | Propósito |
|---:|---|---|
| 00 | `00_preflight.cypher` | Verificar conexión, versión y base activa |
| 01 | `01_constraints.cypher` | Restricciones e índices |
| 02 | `02_nodes_core.cypher` | Personas, departamentos, roles, proyectos y documentos |
| 03 | `03_nodes_technical.cypher` | Repositorios, componentes, servicios, APIs y decisiones |
| 04 | `04_relationships_core.cypher` | Relaciones organizacionales y documentales |
| 05 | `05_dependencies.cypher` | Dependencias técnicas e impacto |
| 06 | `06_governance.cypher` | Solicitudes, aprobaciones, excepciones y escalamiento |
| 07 | `07_security_sync_audit.cypher` | Políticas, sincronización y auditoría |
| 08 | `08_queries.cypher` | Consultas de demostración |
| 09 | `09_tests.cypher` | Pruebas de integridad y cardinalidad |

## Límites técnicos importantes

- Las restricciones de unicidad sí se aplican en Neo4j. Las cardinalidades como “exactamente un líder” no se expresan como restricciones nativas generales; el MVP las comprueba con consultas y debe hacerlas cumplir en una transacción de aplicación.
- Las horas hábiles no se calculan de forma fiable con `duration()` sin un calendario laboral. El MVP almacena `fechaLimite` ya calculada y valida vencimiento con `datetime()`.
- El control de acceso por clasificación se representa en el grafo. Neo4j Community no sustituye un servicio de autorización de aplicación ni el control granular disponible en otras ediciones.
- APOC solo es requisito para la inspección de esquema del servidor Neo4j MCP. Los scripts del MVP no dependen de APOC.
- La carga fue ejecutada el 12 de noviembre de 2026 en la instancia local autorizada `nahl-1`, base `nexuskm`, con Neo4j Enterprise 2026.10.2. La instancia quedó con autenticación habilitada.

## Evidencia de ejecución

La ejecución produjo 63 nodos, 87 relaciones, 23 etiquetas, 33 tipos de relación y 24 restricciones. Las pruebas T1 a T9 no devolvieron violaciones. Q3 confirmó el recorrido desde `Inventory API` hasta `checkout-service`, `Adaptador de pagos`, `checkout-api` y `Sistema Checkout`.

La carpeta `evidencias/` contiene el resumen verificable, resultados de consultas y pruebas, además de visualizaciones reconstruidas a partir de los resultados reales. No son capturas de la interfaz de Neo4j.

## Fuentes de referencia

Consulta `FUENTES.md` para documentación oficial de Neo4j MCP y Codex MCP.
