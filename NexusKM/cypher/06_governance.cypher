// NexusKM 06 - solicitudes, doble aprobación, excepción y escalamiento.
MERGE (s:SolicitudCambio {solicitudId:'SOL-001'})
SET s.titulo='Publicar modelo de amenazas checkout', s.estado='APROBADA',
    s.criticidad='ALTA', s.creadaEn=datetime('2026-11-10T09:00:00-06:00'),
    s.fechaLimite=datetime('2026-11-13T09:00:00-06:00');
MATCH (s:SolicitudCambio {solicitudId:'SOL-001'}), (v:VersionDocumento {versionId:'VER-003'})
MERGE (s)-[:SOBRE]->(v);
MATCH (u:Persona {personaId:'PER-005'}), (s:SolicitudCambio {solicitudId:'SOL-001'})
MERGE (u)-[:SOLICITA]->(s);

UNWIND [
  {id:'APR-001', tipo:'TECNICA', decision:'APROBADA', fecha:'2026-11-10T12:00:00-06:00', persona:'PER-003'},
  {id:'APR-002', tipo:'TECNICA', decision:'APROBADA', fecha:'2026-11-10T14:00:00-06:00', persona:'PER-006'},
  {id:'APR-003', tipo:'SEGURIDAD', decision:'APROBADA', fecha:'2026-11-10T16:00:00-06:00', persona:'PER-002'},
  {id:'APR-004', tipo:'PROPIETARIO', decision:'APROBADA', fecha:'2026-11-10T17:00:00-06:00', persona:'PER-002'}
] AS row
MERGE (a:Aprobacion {aprobacionId:row.id})
SET a.tipo=row.tipo, a.decision=row.decision, a.fecha=datetime(row.fecha)
WITH a,row
MATCH (s:SolicitudCambio {solicitudId:'SOL-001'}), (p:Persona {personaId:row.persona})
MERGE (a)-[:APRUEBA_SOLICITUD]->(s)
MERGE (a)-[:EMITIDA_POR]->(p);

MERGE (e:ExcepcionEmergencia {excepcionId:'EXC-001'})
SET e.motivo='Mitigación temporal mientras se publica el runbook',
    e.criticidad='CRITICA', e.estado='VIGENTE',
    e.inicio=datetime('2026-11-11T09:00:00-06:00'),
    e.fechaLimite=datetime('2026-11-13T09:00:00-06:00'),
    e.horasHabilesAprobadas=48;
MATCH (e:ExcepcionEmergencia {excepcionId:'EXC-001'}),
      (s:SolicitudCambio {solicitudId:'SOL-001'}),
      (p:Persona {personaId:'PER-002'})
MERGE (e)-[:AUTORIZA_TEMPORALMENTE]->(s)
MERGE (e)-[:AUTORIZADA_POR]->(p);

MERGE (d:Delegacion {delegacionId:'DEL-001'})
SET d.desde=datetime('2026-11-12T08:00:00-06:00'),
    d.hasta=datetime('2026-11-14T18:00:00-06:00'), d.estado='ACTIVA';
MATCH (d:Delegacion {delegacionId:'DEL-001'}),
      (o:Persona {personaId:'PER-002'}), (r:Persona {personaId:'PER-004'})
MERGE (d)-[:DE]->(o)
MERGE (d)-[:A]->(r);

MERGE (c:Conflicto {conflictoId:'CONF-001'})
SET c.tipo='SEGREGACION_FUNCIONES', c.estado='RESUELTO',
    c.descripcion='El solicitante no puede emitir aprobación técnica de su propia solicitud';
MATCH (c:Conflicto {conflictoId:'CONF-001'}), (s:SolicitudCambio {solicitudId:'SOL-001'})
MERGE (c)-[:DETECTADO_EN]->(s);

MERGE (e:Escalamiento {escalamientoId:'ESC-001'})
SET e.motivo='Excepción crítica próxima a vencer', e.estado='PENDIENTE',
    e.creadoEn=datetime('2026-11-12T09:00:00-06:00');
MATCH (e:Escalamiento {escalamientoId:'ESC-001'}),
      (x:ExcepcionEmergencia {excepcionId:'EXC-001'}),
      (p:Persona {personaId:'PER-004'})
MERGE (e)-[:GENERADO_POR]->(x)
MERGE (e)-[:DIRIGIDO_A]->(p);
