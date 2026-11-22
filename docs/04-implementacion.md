# 4 Implementación de las tres bases

La unidad reproducible es [compose.yaml](../compose.yaml). Las imágenes se fijan por digest y [requirements-lock.txt](../requirements-lock.txt) fija las dependencias Python. El arranque genera secretos locales si faltan, crea estructuras, carga los IDs compartidos y sincroniza el contenido y las proyecciones.

## Inventario de scripts

| Componente | Archivos | Responsabilidad |
| --- | --- | --- |
| SQL | `database/relational/schema.sql` | Tablas, PK, FK, CHECK e índices |
| Carga integrada | `scripts/bootstrap.py` | Seed SQL, contenido y grafo, marcador de inicialización y outbox |
| Consultas SQL | `database/relational/queries.sql` | S1–S5 catálogo, revisión, vigencia, pendientes y auditoría |
| Mongo | `database/document/validator.json`, `seed.json`, `queries.js` | Validación, tres agregados y D1–D4 |
| Neo4j | `NexusKM/cypher/00_preflight.cypher` a `09_tests.cypher` | Preflight, esquema, carga, relaciones, Q1–Q9 y T1–T13 |
| Conexión y pruebas | `backend/repositories/`, `tests/` | Drivers oficiales e integridad real |
| Evidencias | `scripts/collect_evidence.py` | Consultas completas, conteos, contrato y tiempos |

La carga SQL se encuentra en Python para calcular hashes de contraseña y fechas relativas sin insertar secretos en un SQL compartido. Ejecuta sentencias parametrizadas dentro de una transacción. Las versiones iniciales vencen 180 días después de la primera inicialización; el reinicio no extiende sus fechas ni sobrescribe cambios.

`bootstrap_state` y un bloqueo asesor impiden resembrar un entorno inicializado. La carga Cypher usa MERGE/SET y es un seed para una base vacía: ejecutarla manualmente sobre una base modificada puede restablecer valores del ejemplo. El arranque normal no lo hace. Se conserva la base anterior y se usa la base `neo4j` de un contenedor independiente.

## Índices y motivo

| Índice | Función |
| --- | --- |
| PK y UNIQUE SQL | Identidad, claves alternas y búsquedas exactas |
| one_current_version | Una versión VIGENTE por documento |
| one_open_request | Una solicitud PENDIENTE o APROBADA por versión |
| document_project | Filtrar documentos activos por proyecto en impacto |
| version_expiration | Consultar vencimientos |
| audit_entity_date | Historia de una entidad ordenada por fecha |
| pending_events | Seleccionar solo pendientes por orden de evento |
| Mongo _id_ | Un agregado único por versión y upsert idempotente |
| Mongo document_versions | Versiones de un documento y revisión |
| Neo4j 24 constraints | IDs de las 23 etiquetas y correo de Persona únicos |
| Neo4j 6 índices explícitos | Búsqueda por estado, nombre o clasificación según el esquema |

La instancia actual cuenta 32 índices Neo4j: 24 asociados a unicidad, seis explícitos y dos índices de búsqueda de tokens. Los índices se justifican por acceso y reglas; no se atribuyen mejoras cuantitativas sin comparar planes.

## Resultado de reconstrucción y evolución

La carga inicial tiene 4 departamentos, 6 personas, 2 proyectos, 3 documentos, 3 versiones, 1 solicitud y 4 aprobaciones. Mongo guarda 3 agregados; el grafo tiene 63 nodos y 87 relaciones. El ensayo posterior en navegador añadió un borrador, lo editó y dio de baja, y publicó SOL-001. Por conservar historial, la instantánea actual tiene 4 documentos SQL, 3 activos, 4 agregados Mongo y 65 nodos con 90 relaciones. Ambos resultados son compatibles y están fechados por separado.

Las pruebas comprueban claves foráneas, rollback y unicidad vigente en SQL; inserciones inválidas y contenido anidado en Mongo; unicidad, cardinalidades, reglas y cobertura positiva en Neo4j. La [evidencia actual](pruebas/evidencias/verificacion-integrada.json) contiene las salidas reales. El ensayo de instalación nueva está registrado en [reconstruccion.json](pruebas/evidencias/reconstruccion.json).
