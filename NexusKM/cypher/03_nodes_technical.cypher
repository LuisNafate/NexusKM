// NexusKM 03 - activos técnicos y decisiones.
UNWIND [
  {id:'REP-001', nombre:'checkout-api', url:'https://example.invalid/checkout-api'},
  {id:'REP-002', nombre:'inventory-api', url:'https://example.invalid/inventory-api'}
] AS row
MERGE (n:Repositorio {repositorioId:row.id})
SET n.nombre=row.nombre, n.url=row.url, n.estado='ACTIVO';

UNWIND [
  {id:'CMP-001', nombre:'Adaptador de pagos', tipo:'MODULO'},
  {id:'CMP-002', nombre:'Reserva de existencias', tipo:'MODULO'},
  {id:'CMP-003', nombre:'Cliente antifraude', tipo:'LIBRERIA'}
] AS row
MERGE (n:Componente {componenteId:row.id})
SET n.nombre=row.nombre, n.tipo=row.tipo, n.estado='ACTIVO';

UNWIND [
  {id:'SRV-001', nombre:'checkout-service', criticidad:'CRITICA'},
  {id:'SRV-002', nombre:'inventory-service', criticidad:'ALTA'},
  {id:'SRV-003', nombre:'fraud-service', criticidad:'CRITICA'}
] AS row
MERGE (n:Microservicio {servicioId:row.id})
SET n.nombre=row.nombre, n.criticidad=row.criticidad, n.estado='ACTIVO';

UNWIND [
  {id:'API-001', nombre:'Payments API', version:'v2', protocolo:'REST'},
  {id:'API-002', nombre:'Inventory API', version:'v1', protocolo:'REST'},
  {id:'API-003', nombre:'Fraud Scoring API', version:'v3', protocolo:'REST'}
] AS row
MERGE (n:API {apiId:row.id})
SET n.nombre=row.nombre, n.version=row.version, n.protocolo=row.protocolo, n.estado='ACTIVA';

UNWIND [
  {id:'DEC-001', titulo:'Usar eventos para reservar inventario', fecha:'2026-08-20', estado:'ACEPTADA'},
  {id:'DEC-002', titulo:'Separar evaluación antifraude', fecha:'2026-09-05', estado:'ACEPTADA'}
] AS row
MERGE (n:Decision {decisionId:row.id})
SET n.titulo=row.titulo, n.fecha=date(row.fecha), n.estado=row.estado;
