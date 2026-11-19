# Evidencia de ejecución de NexusKM

Fecha: 12 de noviembre de 2026  
Instancia: `nahl-1`  
Base: `nexuskm`  
Motor: Neo4j Enterprise 2026.10.2  
Conexión usada: Bolt local en `127.0.0.1:7687`

## Carga ejecutada

Los archivos `00_preflight.cypher` a `07_security_sync_audit.cypher` finalizaron con código de salida 0. Después se ejecutaron `08_queries.cypher` y `09_tests.cypher`, también con código de salida 0.

## Estado resultante

| Indicador | Resultado |
|---|---:|
| Nodos | 63 |
| Relaciones | 87 |
| Etiquetas | 23 |
| Tipos de relación | 33 |
| Restricciones | 24 |
| Índices totales | 30 |

Los 30 índices incluyen los índices que respaldan restricciones y 6 índices de búsqueda declarados de forma explícita.

## Seguridad de la instancia

La autenticación se restauró y quedó habilitada después de actualizar la credencial autorizada. Las bases `system`, `neo4j` y `nexuskm` permanecieron en línea. No se eliminaron bases ni datos existentes.

## Interpretación

Esta evidencia confirma que NexusKM dejó de ser únicamente una propuesta documental. El conjunto ficticio y su esquema fueron cargados en la instancia indicada. Las funciones fuera del MVP continúan sin implementarse: interfaz web, SSO, conectores productivos, notificaciones, calendario automático de horas hábiles y controles completos de una aplicación.
