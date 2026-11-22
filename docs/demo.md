# Guion de demostración de NexusKM

Duración sugerida: 8–10 minutos. Inicia Compose y abre localhost:58000. Usa las identidades ficticias y DEMO_PASSWORD de `.env`; no muestres el archivo ni el token durante una grabación.

| Tiempo | Acción | Qué demuestra |
| --- | --- | --- |
| 0–1 min | Presentar problema y asignación SQL/Mongo/grafo | Uso justificado de tres modelos |
| 1–2 min | Carlos PER-002, Impacto, Inventory API | Neo4j encuentra el camino; SQL y Mongo completan documentos |
| 2–3 min | Sofía PER-005, crear runbook INTERNO para CHECKOUT | Alta en los tres motores y contenido tipado |
| 3–4 min | Abrir borrador, editar contenido y título | Mongo actualiza contenido; revisión evita sobrescritura |
| 4–5 min | Crear solicitud de revisión como Sofía | BORRADOR → EN_REVISION; contenido deja de ser editable |
| 5–6 min | Laura PER-003 y Diego PER-006 aprueban TECNICA | Dos revisores distintos; solicitante no se autoaprueba técnicamente |
| 6–7 min | Sofía emite PROPIETARIO y publica | Transacción SQL, contenido Mongo y proyección Neo4j |
| 7–8 min | Volver a Impacto y consultar auditoría con Carlos | Versión publicada aparece por proyecto y permisos; trazabilidad |
| 8–9 min | Crear otro borrador propio y darlo de baja | Elimina del catálogo activo y conserva historial |
| 9–10 min | Mostrar JUnit, estado de motores y recuperación | Evidencia actual, 39 pruebas y consistencia eventual |

Para documento SEGURIDAD/RESTRINGIDO también debe aprobar Carlos como SEGURIDAD y el propietario real como PROPIETARIO. SOL-001 viene APROBADA en una instalación nueva para facilitar publicar con Carlos; en la instancia de evidencias ya está PUBLICADA, por lo que se usa el flujo nuevo de la tabla para repetir.

La prueba de fallo parcial está automatizada: ejecutar `scripts/test.ps1` y explicar el caso correspondiente sin interrumpir manualmente las bases durante la demostración. Mostrar `synchronization.pending` y panel de ADMIN cuando se desee revisar el mecanismo.
