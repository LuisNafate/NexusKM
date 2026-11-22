// NexusKM 02 - núcleo organizacional y conocimiento.
UNWIND [
  {id:'DEP-001', nombre:'Desarrollo', descripcion:'Construcción y mantenimiento de software'},
  {id:'DEP-002', nombre:'Seguridad', descripcion:'Seguridad de aplicaciones y cumplimiento'},
  {id:'DEP-003', nombre:'Arquitectura', descripcion:'Arquitectura empresarial y estándares'},
  {id:'DEP-004', nombre:'Operaciones', descripcion:'Disponibilidad y operación de plataformas'}
] AS row
MERGE (n:Departamento {departamentoId:row.id})
SET n.nombre=row.nombre, n.descripcion=row.descripcion, n.estado='ACTIVO';

UNWIND [
  {id:'PER-001', nombre:'Ana López', correo:'ana.lopez@nexuskm.test'},
  {id:'PER-002', nombre:'Carlos Ruiz', correo:'carlos.ruiz@nexuskm.test'},
  {id:'PER-003', nombre:'Laura García', correo:'laura.garcia@nexuskm.test'},
  {id:'PER-004', nombre:'Miguel Torres', correo:'miguel.torres@nexuskm.test'},
  {id:'PER-005', nombre:'Sofía Herrera', correo:'sofia.herrera@nexuskm.test'},
  {id:'PER-006', nombre:'Diego Pérez', correo:'diego.perez@nexuskm.test'}
] AS row
MERGE (n:Persona {personaId:row.id})
SET n.nombre=row.nombre, n.correo=row.correo, n.estado='ACTIVO';

UNWIND [
  {id:'ROL-001', nombre:'Líder de proyecto'},
  {id:'ROL-002', nombre:'Arquitecto técnico'},
  {id:'ROL-003', nombre:'Revisor de seguridad'},
  {id:'ROL-004', nombre:'Propietario documental'},
  {id:'ROL-005', nombre:'Administrador de conocimiento'}
] AS row
MERGE (n:Rol {rolId:row.id})
SET n.nombre=row.nombre, n.descripcion='Responsabilidad de ' + row.nombre;

UNWIND [
  {id:'PRY-001', codigo:'CHECKOUT', nombre:'Sistema Checkout', descripcion:'Compras y pagos'},
  {id:'PRY-002', codigo:'INVENTARIO', nombre:'Sistema Inventario', descripcion:'Existencias y disponibilidad'}
] AS row
MERGE (n:Proyecto {proyectoId:row.id})
SET n.codigo=row.codigo, n.nombre=row.nombre, n.descripcion=row.descripcion, n.estado='ACTIVO';

UNWIND [
  {id:'CON-001', nombre:'Operación de pagos', tipo:'OPERATIVO', estado:'VIGENTE'},
  {id:'CON-002', nombre:'Contrato de inventario', tipo:'TECNICO', estado:'VIGENTE'},
  {id:'CON-003', nombre:'Respuesta a incidentes', tipo:'SEGURIDAD', estado:'VIGENTE'}
] AS row
MERGE (n:Conocimiento {conocimientoId:row.id})
SET n.nombre=row.nombre, n.tipo=row.tipo, n.estado=row.estado;

UNWIND [
  {id:'DOC-001', titulo:'Runbook de pagos', tipo:'RUNBOOK', clasificacion:'INTERNO', estado:'PUBLICADO'},
  {id:'DOC-002', titulo:'Contrato API de inventario', tipo:'API', clasificacion:'INTERNO', estado:'PUBLICADO'},
  {id:'DOC-003', titulo:'Modelo de amenazas checkout', tipo:'SEGURIDAD', clasificacion:'RESTRINGIDO', estado:'EN_REVISION'}
] AS row
MERGE (n:Documento {documentoId:row.id})
SET n.titulo=row.titulo, n.tipo=row.tipo, n.clasificacion=row.clasificacion, n.estado=row.estado;

UNWIND [
  {id:'VER-001', numero:'1.0', estado:'VIGENTE', publicada:'2026-09-01T09:00:00-06:00', vence:'2027-03-01T09:00:00-06:00'},
  {id:'VER-002', numero:'2.1', estado:'VIGENTE', publicada:'2026-10-15T12:00:00-06:00', vence:'2027-04-15T12:00:00-06:00'},
  {id:'VER-003', numero:'0.9', estado:'BORRADOR', publicada:null, vence:'2026-11-14T17:00:00-06:00'}
] AS row
MERGE (n:VersionDocumento {versionId:row.id})
SET n.numero=row.numero, n.estado=row.estado,
    n.fechaPublicacion=CASE WHEN row.publicada IS NULL THEN null ELSE datetime(row.publicada) END,
    n.fechaVencimiento=datetime(row.vence);
