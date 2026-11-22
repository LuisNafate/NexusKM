-- S1. Catálogo con responsable y proyecto.
SELECT d.document_id,d.title,p.name AS project,u.name AS owner
FROM documents d JOIN projects p USING(project_id)
JOIN people u ON u.person_id=d.owner_id WHERE d.active ORDER BY d.title;

-- S2. Aprobaciones por solicitud y persona.
SELECT r.request_id,r.state,a.kind,p.name
FROM change_requests r LEFT JOIN approvals a USING(request_id)
LEFT JOIN people p ON p.person_id=a.reviewer_id ORDER BY r.request_id,a.kind;

-- S3. Publicaciones vigentes y fechas.
SELECT d.document_id,d.title,v.version_id,v.number,v.expires_at
FROM documents d JOIN versions v USING(document_id)
WHERE d.active AND v.state='VIGENTE' AND v.expires_at>now();

-- S4. Recuperación de escrituras parciales.
SELECT event_id,document_id,state,attempts,last_error FROM outbox
WHERE state='PENDIENTE' ORDER BY event_id;

-- S5. Historial de cambios.
SELECT action,entity_id,actor_id,created_at FROM audit_events ORDER BY event_id DESC LIMIT 20;
