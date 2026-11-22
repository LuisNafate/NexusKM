// NexusKM 05 - dependencias explícitas y trazables.
UNWIND [
  {id:'DEPTEC-001', tipo:'API', criticidad:'CRITICA', descripcion:'Checkout consume inventario antes de confirmar pago'},
  {id:'DEPTEC-002', tipo:'API', criticidad:'CRITICA', descripcion:'Checkout consulta puntuación antifraude'},
  {id:'DEPTEC-003', tipo:'DATOS', criticidad:'ALTA', descripcion:'Runbook depende del contrato vigente de Payments API'}
] AS row
MERGE (n:RegistroDependencia {dependenciaId:row.id})
SET n.tipo=row.tipo, n.criticidad=row.criticidad, n.descripcion=row.descripcion, n.estado='ACTIVA';

MATCH (r:RegistroDependencia {dependenciaId:'DEPTEC-001'}),
      (o:Microservicio {servicioId:'SRV-001'}),
      (d:API {apiId:'API-002'})
MERGE (r)-[:DESDE]->(o)
MERGE (r)-[:HACIA]->(d);

MATCH (r:RegistroDependencia {dependenciaId:'DEPTEC-002'}),
      (o:Microservicio {servicioId:'SRV-001'}),
      (d:API {apiId:'API-003'})
MERGE (r)-[:DESDE]->(o)
MERGE (r)-[:HACIA]->(d);

MATCH (r:RegistroDependencia {dependenciaId:'DEPTEC-003'}),
      (o:Documento {documentoId:'DOC-001'}),
      (d:API {apiId:'API-001'})
MERGE (r)-[:DESDE]->(o)
MERGE (r)-[:HACIA]->(d);

MATCH (s:Microservicio {servicioId:'SRV-001'}), (a:API {apiId:'API-002'})
MERGE (s)-[r:DEPENDE_DE {dependenciaId:'DEPTEC-001'}]->(a)
SET r.criticidad='CRITICA';
MATCH (s:Microservicio {servicioId:'SRV-001'}), (a:API {apiId:'API-003'})
MERGE (s)-[r:DEPENDE_DE {dependenciaId:'DEPTEC-002'}]->(a)
SET r.criticidad='CRITICA';
