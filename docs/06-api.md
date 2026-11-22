# 6 Backend y API REST

La API usa JSON y acciones HTTP explícitas. REST resulta suficiente para un conjunto conocido de operaciones y permite revisar el contrato mediante Swagger en `/docs`. El [OpenAPI exportado](api/openapi.json) documenta campos, restricciones y cabeceras desde el mismo código ejecutado.

## Capas

| Capa | Archivos | Responsabilidad |
| --- | --- | --- |
| Entrada HTTP | backend/api.py, models.py | Rutas, validación Pydantic y serialización |
| Identidad | backend/auth.py | PBKDF2, token firmado y usuario SQL activo |
| Dominio | backend/service.py | Permisos, revisión, aprobación, publicación e idempotencia |
| Integración | backend/synchronization.py | Outbox, orden, upsert y snapshot del grafo |
| Persistencia | backend/repositories/ | psycopg 3, PyMongo y Neo4j Python Driver |
| Ciclo de vida | backend/launch.py, main.py | Bootstrap, worker, servidor y errores |

## Rutas

Todas las rutas de la tabla llevan prefijo `/api`. UUID indica la cabecera `Idempotency-Key`.

| Método y ruta | Datos | Permiso |
| --- | --- | --- |
| GET /health | Sin cuerpo | Público; 200 tres motores sanos o 503 |
| POST /auth/login | person_id, password | Público |
| GET /me | Bearer | Usuario activo |
| GET /catalog | Bearer | Usuario activo |
| GET /documents | Bearer | Filtrado por clasificación |
| GET /documents/{id} | Bearer | Lectura autorizada |
| POST /documents | DocumentInput y UUID | Propietario propio o ADMIN |
| PATCH /documents/{id} | title, expected_revision, UUID | Propietario o ADMIN |
| DELETE /documents/{id} | expected_revision en query, UUID | Propietario o ADMIN; baja permitida |
| POST /documents/{id}/versions | VersionInput y UUID | Propietario o ADMIN |
| PUT /versions/{id}/content | content, expected_revision, UUID | Propietario o ADMIN; BORRADOR |
| GET /requests | Bearer | Filtrado por documento |
| POST /requests | version_id y UUID | Propietario o ADMIN |
| POST /requests/{id}/approvals | kind y UUID | Según identidad/rol de aprobación |
| POST /requests/{id}/publish | UUID | Propietario o ADMIN; requisitos completos |
| GET /impact/{api_id} | Bearer | Contenido filtrado por clasificación |
| GET /audit | Bearer | Eventos propios; ADMIN/SEGURIDAD todos |
| GET /synchronization | Bearer | ADMIN |
| POST /synchronization/retry | Sin cuerpo | ADMIN; reintento idempotente de eventos |

El reintento administrativo no crea una intención de negocio y no exige UUID. Los comandos de negocio sí lo exigen. Las respuestas de comando incluyen `operation_id`, IDs afectados, `replayed` y `synchronization`.

## Ejemplo de alta

```json
{
  "title": "Runbook de recuperación",
  "kind": "RUNBOOK",
  "classification": "INTERNO",
  "owner_id": "PER-005",
  "project_id": "PRY-001",
  "number": "1.0",
  "expires_at": "2027-06-01T12:00:00-06:00",
  "content": {
    "summary": "Procedimiento de recuperación de la operación de pagos.",
    "sections": [{"heading": "Alcance", "body": "Servicio de Checkout."}],
    "steps": [{"title": "Revisar", "instruction": "Comprobar disponibilidad de inventario."}]
  }
}
```

Usar `Authorization: Bearer <token local>` y `Idempotency-Key: <UUID nuevo>`. Los marcadores son contratos de ejemplo, no secretos. En una instalación futura ajustar el vencimiento para que siga siendo posterior al momento de la operación.

## Validación y errores

El título tiene 3–160 caracteres; número de versión usa dos o tres componentes numéricos; fechas incluyen zona y son futuras; las revisiones son enteros positivos. El contenido exige resumen, secciones y un arreglo propio del tipo. Pydantic prohíbe campos superiores desconocidos; el servidor determina actor, estado e IDs nuevos.

| Estado | Significado |
| --- | --- |
| 200 / 201 | Consulta o comando completado; creación cuando corresponde |
| 202 | Commit de negocio confirmado y sincronización pendiente |
| 401 | Identidad, contraseña o token inválido/vencido |
| 403 | Usuario autenticado sin permiso |
| 404 | Entidad inexistente o documento inactivo |
| 409 | Revisión, unicidad, estado, idempotencia o sincronización en conflicto |
| 422 | Cuerpo, cabecera, fecha o contenido inválidos |
| 503 | Base no disponible durante una consulta o escritura previa al commit |

Las excepciones de driver se traducen sin devolver conexión o contraseña. Si el commit SQL ya existe y falla una proyección, se reporta pendiente y se recupera desde outbox. Los detalles internos se limitan al nombre de la clase de error en la cola.

## Permisos implementados

Todos los usuarios activos leen INTERNO. RESTRINGIDO admite propietario y roles TECNICO, SEGURIDAD o ADMIN. El propietario o ADMIN edita metadatos y borradores. Solo TECNICO distinto del solicitante aprueba técnicamente; SEGURIDAD emite su aprobación; la aprobación PROPIETARIO requiere identidad exacta del dueño incluso para ADMIN. Un mismo usuario puede ser propietario y seguridad; las dos aprobaciones técnicas siempre provienen de personas distintas. Esta es una política de alcance explícita, no separación absoluta de todos los roles.

Los tokens firmados son propios de esta aplicación y no se presentan como OAuth empresarial o JWT estándar. La interfaz conserva sesión en memoria del navegador y no contiene credenciales embebidas. Los seis usuarios comparten la contraseña de demostración generada en `.env` en la primera carga; cambiarla después requiere una política de cambio de contraseña que esta versión no implementa.
