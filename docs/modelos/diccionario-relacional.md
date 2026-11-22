# Diccionario relacional completo

Esquema consultado en PostgreSQL 16 el 21 de noviembre de 2026. NOT NULL se expresa como obligatorio; las PK también son únicas. Las FK usan la política predeterminada de restricción de referencias; no se aplican cascadas de borrado.

## approvals

| Campo | Tipo SQL | Obligatorio | Clave | Predeterminado |
| --- | --- | --- | --- | --- |
| approval_id | text | Sí | PK | Sin valor |
| request_id | text | Sí | FK → change_requests.request_id | Sin valor |
| reviewer_id | text | Sí | FK → people.person_id | Sin valor |
| kind | text | Sí | — | Sin valor |
| created_at | timestamp with time zone | Sí | — | now() |

## audit_events

| Campo | Tipo SQL | Obligatorio | Clave | Predeterminado |
| --- | --- | --- | --- | --- |
| event_id | bigint | Sí | PK | IDENTITY |
| actor_id | text | No | FK → people.person_id | Sin valor |
| action | text | Sí | — | Sin valor |
| entity_id | text | Sí | — | Sin valor |
| details | jsonb | Sí | — | '{}'::jsonb |
| created_at | timestamp with time zone | Sí | — | now() |

## bootstrap_state

| Campo | Tipo SQL | Obligatorio | Clave | Predeterminado |
| --- | --- | --- | --- | --- |
| key | text | Sí | PK | Sin valor |
| initialized_at | timestamp with time zone | Sí | — | now() |

## change_requests

| Campo | Tipo SQL | Obligatorio | Clave | Predeterminado |
| --- | --- | --- | --- | --- |
| request_id | text | Sí | PK | Sin valor |
| version_id | text | Sí | FK → versions.version_id | Sin valor |
| requester_id | text | Sí | FK → people.person_id | Sin valor |
| state | text | Sí | — | 'PENDIENTE'::text |
| created_at | timestamp with time zone | Sí | — | now() |

## departments

| Campo | Tipo SQL | Obligatorio | Clave | Predeterminado |
| --- | --- | --- | --- | --- |
| department_id | text | Sí | PK | Sin valor |
| name | text | Sí | UNIQUE | Sin valor |
| description | text | Sí | — | Sin valor |

## documents

| Campo | Tipo SQL | Obligatorio | Clave | Predeterminado |
| --- | --- | --- | --- | --- |
| document_id | text | Sí | PK | Sin valor |
| title | text | Sí | — | Sin valor |
| kind | text | Sí | — | Sin valor |
| classification | text | Sí | — | Sin valor |
| owner_id | text | Sí | FK → people.person_id | Sin valor |
| project_id | text | Sí | FK → projects.project_id | Sin valor |
| active | boolean | Sí | — | true |
| revision | integer | Sí | — | 1 |

## operations

| Campo | Tipo SQL | Obligatorio | Clave | Predeterminado |
| --- | --- | --- | --- | --- |
| operation_id | uuid | Sí | PK | Sin valor |
| actor_id | text | Sí | FK → people.person_id | Sin valor |
| action | text | Sí | — | Sin valor |
| request_hash | text | Sí | — | Sin valor |
| response | jsonb | Sí | — | Sin valor |
| created_at | timestamp with time zone | Sí | — | now() |

## outbox

| Campo | Tipo SQL | Obligatorio | Clave | Predeterminado |
| --- | --- | --- | --- | --- |
| event_id | bigint | Sí | PK | IDENTITY |
| document_id | text | Sí | FK → documents.document_id | Sin valor |
| action | text | Sí | — | Sin valor |
| payload | jsonb | No | — | Sin valor |
| state | text | Sí | — | 'PENDIENTE'::text |
| attempts | integer | Sí | — | 0 |
| last_error | text | No | — | Sin valor |
| created_at | timestamp with time zone | Sí | — | now() |
| completed_at | timestamp with time zone | No | — | Sin valor |

## people

| Campo | Tipo SQL | Obligatorio | Clave | Predeterminado |
| --- | --- | --- | --- | --- |
| person_id | text | Sí | PK | Sin valor |
| name | text | Sí | — | Sin valor |
| email | text | Sí | UNIQUE | Sin valor |
| department_id | text | Sí | FK → departments.department_id | Sin valor |
| role | text | Sí | — | Sin valor |
| password_hash | text | Sí | — | Sin valor |
| active | boolean | Sí | — | true |

## projects

| Campo | Tipo SQL | Obligatorio | Clave | Predeterminado |
| --- | --- | --- | --- | --- |
| project_id | text | Sí | PK | Sin valor |
| code | text | Sí | UNIQUE | Sin valor |
| name | text | Sí | — | Sin valor |
| department_id | text | Sí | FK → departments.department_id | Sin valor |
| leader_id | text | Sí | FK → people.person_id | Sin valor |
| active | boolean | Sí | — | true |

## versions

| Campo | Tipo SQL | Obligatorio | Clave | Predeterminado |
| --- | --- | --- | --- | --- |
| version_id | text | Sí | PK | Sin valor |
| document_id | text | Sí | FK → documents.document_id | Sin valor |
| number | text | Sí | — | Sin valor |
| state | text | Sí | — | Sin valor |
| expires_at | timestamp with time zone | Sí | — | Sin valor |
| published_at | timestamp with time zone | No | — | Sin valor |
| content_revision | integer | Sí | — | 1 |

## Dominios y claves compuestas

people.role: LIDER, TECNICO, SEGURIDAD, PROPIETARIO, ADMIN. documents.kind: RUNBOOK, API, SEGURIDAD; classification: INTERNO o RESTRINGIDO. versions.state: BORRADOR, EN_REVISION, VIGENTE o RETIRADA. change_requests.state: PENDIENTE, APROBADA, PUBLICADA o CANCELADA. approvals.kind: TECNICA, SEGURIDAD o PROPIETARIO. outbox.action: SYNC o DELETE; state: PENDIENTE o COMPLETA.

revision y content_revision son positivos; título tiene longitud recortada 3–160. UNIQUE(document_id, number) evita duplicar números de versión. UNIQUE(request_id, reviewer_id, kind) evita repetir una aprobación por persona y tipo. Los índices únicos parciales limitan una VIGENTE por documento y una solicitud abierta por versión. Auditoría admite actor nulo para eventos del sistema; las acciones humanas se insertan con actor explícito. outbox.payload es transitorio y se limpia tras completar la entrega.
