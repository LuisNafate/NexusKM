# 5 Catálogo de operaciones y consultas

Las rutas devuelven JSON. Todas requieren identidad salvo salud y login. Los comandos documentales y de gobernanza exigen `Idempotency-Key` UUID; creación responde 201, cambio 200 o 202 cuando la sincronización queda pendiente. El contrato exacto está en [OpenAPI](api/openapi.json).

## Operaciones funcionales

| ID | Propósito y bases | Entrada y validaciones | Salida normal | Límite o error comprobado |
| --- | --- | --- | --- | --- |
| O01 | Login · SQL | person_id o correo y password, usuario activo | Token de una hora y persona | Contraseña errónea o token alterado/vencido: 401 |
| O02 | Catálogo · SQL y grafo | Identidad válida | Proyectos, personas y APIs con IDs | Acceso anónimo: 401 |
| O03 | Alta documental · tres bases | Título, tipo, clasificación, propietario, proyecto, número, vencimiento y contenido tipado | IDs DOC/VER, revisión, sincronización | Propietario ajeno: 403; FK inexistente: 409; contenido inválido: 422 |
| O04 | Lista y detalle · SQL y Mongo | document_id; permiso de lectura | Metadatos, versiones, contenido y content_ready | Recurso inexistente o inactivo: 404; restringido ajeno: 403 |
| O05 | Cambiar título · SQL y grafo | title, expected_revision | Revisión incrementada | Revisión obsoleta: 409; no propietario/admin: 403 |
| O06 | Nueva versión · tres bases | Número, fecha futura, contenido acorde al tipo | Nuevo version_id BORRADOR | Número duplicado por documento: 409; fecha sin zona o pasada: 422 |
| O07 | Editar contenido · tres bases | content y expected_revision de contenido | Revisión incrementada y agregado actualizado | Versión EN_REVISION/VIGENTE: 409; estructura anidada inválida: 422 |
| O08 | Baja lógica · SQL y grafo | ID y expected_revision en query | INACTIVO; conserva Mongo e historial | Publicación vigente o solicitud abierta: 409 |
| O09 | Solicitar revisión · SQL y grafo | version_id en BORRADOR, propietario/admin | SOL PENDIENTE; versión EN_REVISION | Versión no borrador o solicitud abierta: 409 |
| O10 | Aprobar · SQL y grafo | request_id y kind | PENDIENTE o APROBADA según requisitos | Técnico solicitante, rol incorrecto o falso propietario: 403; duplicado: 409 |
| O11 | Publicar · tres bases | request_id, propietario/admin | PUBLICADA, versión VIGENTE; anterior RETIRADA | Aprobaciones incompletas/contenido pendiente: 409; vencimiento: 422 |
| O12 | Impacto · tres bases | api_id; lectura por rol | Caminos, proyectos, documentos vigentes y fuentes | API desconocida: 404; API sin consumidores: lista vacía válida |
| O13 | Auditoría · SQL | Identidad | Últimos 100 eventos propios; ADMIN/SEGURIDAD ven todos | Usuario ordinario no ve eventos ajenos |
| O14 | Consultar/reintentar sincronización · tres bases | ADMIN, POST de reintento | Pendientes, intentos y resultado | No ADMIN: 403; recuperación no duplica contenido ni nodos |

Repetir la misma intención con su UUID devuelve el mismo resultado de dominio; usarlo con cuerpo, actor o acción distintos produce 409. La fecha usa ISO 8601 con zona horaria. `content_ready` exige que la revisión del contenido coincida con la revisión oficial SQL.

## Consultas por modelo

| ID | Pregunta y entidades | Parámetros o filtro | Resultado y casos relevantes |
| --- | --- | --- | --- |
| S1 | Catálogo con proyecto y propietario · 3 tablas | active=true | Actualmente 3 activos; la baja no aparece |
| S2 | Solicitud, aprobaciones y revisores · 3 tablas | Todas las solicitudes | SOL-001 con 4 aprobaciones |
| S3 | Documentos con versión vigente · 2 tablas | VIGENTE y expires_at mayor que now | Excluye borradores, inactivos y vencidos |
| S4 | Pendientes de recuperación | state=PENDIENTE | Cero al cerrar verificación; aumenta en fallo inyectado |
| S5 | Historial | Últimos 20 eventos | Actor, acción, entidad y fecha |
| D1 | Contenido completo de versión | _id=VER-001 | Agregado del runbook; ID ajeno devuelve ausencia |
| D2 | Versiones de un documento | documentId=DOC-001 | Proyección de ID, tipo, revisión y resumen |
| D3 | Runbooks con pasos anidados | RUNBOOK y steps.0 existe | Incluye historial retenido; SQL decide si está activo |
| D4 | Contratos con GET | API y endpoints.method=GET | Contrato de Inventory API |
| Q1 | Líder y departamento del proyecto · 3 etiquetas | Catálogo completo | CHECKOUT y INVENTARIO con responsables |
| Q2 | Documentación vigente · 4 etiquetas | PUBLICADO, activo, VIGENTE y no vencida | Dos versiones iniciales; tres tras publicar SOL-001 |
| Q3 | Impacto API · 6 etiquetas | API-002 en ejemplo; API parametrizada en backend | checkout-service, Adaptador de pagos, CHECKOUT |
| Q4 | Técnicos distintos · 3 etiquetas | Aprobaciones TECNICA APROBADA | Laura y Diego; conteo 2 |
| Q5 | Riesgo temporal de excepción | Estados y fecha límite | EXC-001 vencida; cerrada tiene prioridad sobre vencimiento |
| Q6 | Auditoría histórica · 2 etiquetas | Orden por fecha | Cinco eventos del seed; auditoría actual se consulta en SQL |
| Q7 | Sincronización histórica en conflicto · 3 etiquetas | CONFLICTO | Ejemplo Confluence; no ejecuta un conector |
| Q8 | Políticas representadas · 3 etiquetas | PER-002 | Lectura restringida; la autorización actual está en el servicio |
| Q9 | Cobertura de etiquetas | Conteos completos | 23 tipos con datos; evita inferir éxito sobre base vacía |

Q1, Q2, Q3, Q4, Q7 y Q8 atraviesan al menos tres entidades. Se superan las cinco consultas y los dos recorridos requeridos por la actividad de grafos. Los archivos SQL/Cypher/JS contienen sentencias legibles; `collect_evidence` ejecuta S1–S5, D1–D4 y Q1–Q9 y conserva parámetros y salidas completas en el JSON de verificación. Los casos negativos y límites se relacionan con pruebas en la [matriz](pruebas/matriz.md).
