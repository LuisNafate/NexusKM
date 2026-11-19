// NexusKM 07 - seguridad representada, sincronización y auditoría.
UNWIND [
  {id:'POL-001', clasificacion:'INTERNO', accion:'LECTURA', rol:'ROL-001'},
  {id:'POL-002', clasificacion:'RESTRINGIDO', accion:'LECTURA', rol:'ROL-003'},
  {id:'POL-003', clasificacion:'RESTRINGIDO', accion:'APROBAR', rol:'ROL-002'}
] AS row
MERGE (p:PoliticaAcceso {politicaId:row.id})
SET p.clasificacion=row.clasificacion, p.accion=row.accion
WITH p,row MATCH (r:Rol {rolId:row.rol}) MERGE (r)-[:HABILITA]->(p);

UNWIND [
  {id:'ORG-001', nombre:'GitHub Enterprise', tipo:'REPOSITORIO'},
  {id:'ORG-002', nombre:'Confluence', tipo:'DOCUMENTACION'}
] AS row
MERGE (o:SistemaOrigen {origenId:row.id}) SET o.nombre=row.nombre, o.tipo=row.tipo;

UNWIND [
  {id:'SYNC-001', inicio:'2026-11-12T06:00:00-06:00', fin:'2026-11-12T06:02:00-06:00', estado:'EXITOSA', origen:'ORG-001'},
  {id:'SYNC-002', inicio:'2026-11-12T06:05:00-06:00', fin:'2026-11-12T06:08:00-06:00', estado:'CONFLICTO', origen:'ORG-002'}
] AS row
MERGE (s:Sincronizacion {sincronizacionId:row.id})
SET s.inicio=datetime(row.inicio), s.fin=datetime(row.fin), s.estado=row.estado
WITH s,row MATCH (o:SistemaOrigen {origenId:row.origen}) MERGE (s)-[:DESDE_ORIGEN]->(o);

MATCH (s:Sincronizacion {sincronizacionId:'SYNC-001'}), (r:Repositorio {repositorioId:'REP-001'})
MERGE (s)-[:ACTUALIZA]->(r);
MATCH (s:Sincronizacion {sincronizacionId:'SYNC-002'}), (d:Documento {documentoId:'DOC-003'})
MERGE (s)-[:ACTUALIZA]->(d);

UNWIND [
  {id:'EVT-001', tipo:'CREACION', entidad:'SolicitudCambio', entidadId:'SOL-001', actor:'PER-005', fecha:'2026-11-10T09:00:00-06:00'},
  {id:'EVT-002', tipo:'APROBACION', entidad:'SolicitudCambio', entidadId:'SOL-001', actor:'PER-003', fecha:'2026-11-10T12:00:00-06:00'},
  {id:'EVT-003', tipo:'APROBACION', entidad:'SolicitudCambio', entidadId:'SOL-001', actor:'PER-006', fecha:'2026-11-10T14:00:00-06:00'},
  {id:'EVT-004', tipo:'EXCEPCION', entidad:'ExcepcionEmergencia', entidadId:'EXC-001', actor:'PER-002', fecha:'2026-11-11T09:00:00-06:00'},
  {id:'EVT-005', tipo:'SINCRONIZACION', entidad:'Documento', entidadId:'DOC-003', actor:'SISTEMA', fecha:'2026-11-12T06:08:00-06:00'}
] AS row
MERGE (e:EventoAuditoria {eventoId:row.id})
SET e.tipo=row.tipo, e.entidad=row.entidad, e.entidadId=row.entidadId, e.fecha=datetime(row.fecha)
WITH e,row OPTIONAL MATCH (p:Persona {personaId:row.actor})
FOREACH (_ IN CASE WHEN p IS NULL THEN [] ELSE [1] END | MERGE (e)-[:EJECUTADO_POR]->(p));
