// NexusKM 04 - relaciones organizacionales, documentales y técnicas.
MATCH (p:Persona), (d:Departamento)
WHERE [p.personaId,d.departamentoId] IN [
  ['PER-001','DEP-001'],['PER-002','DEP-002'],['PER-003','DEP-003'],
  ['PER-004','DEP-004'],['PER-005','DEP-001'],['PER-006','DEP-003']]
MERGE (p)-[:PERTENECE_A]->(d);

MATCH (p:Persona), (r:Rol)
WHERE [p.personaId,r.rolId] IN [
  ['PER-001','ROL-001'],['PER-002','ROL-003'],['PER-003','ROL-002'],
  ['PER-004','ROL-005'],['PER-005','ROL-004'],['PER-006','ROL-002']]
MERGE (p)-[:TIENE_ROL]->(r);

MATCH (p:Persona), (d:Departamento)
WHERE [p.personaId,d.departamentoId] IN [
  ['PER-001','DEP-001'],['PER-002','DEP-002'],['PER-003','DEP-003'],['PER-004','DEP-004']]
MERGE (p)-[:DIRIGE]->(d);

MATCH (p:Proyecto), (d:Departamento)
WHERE [p.proyectoId,d.departamentoId] IN [['PRY-001','DEP-001'],['PRY-002','DEP-003']]
MERGE (p)-[:PROPIEDAD_DE]->(d);

MATCH (u:Persona), (p:Proyecto)
WHERE [u.personaId,p.proyectoId] IN [['PER-001','PRY-001'],['PER-003','PRY-002']]
MERGE (u)-[:LIDERA]->(p);

MATCH (u:Persona), (p:Proyecto)
WHERE [u.personaId,p.proyectoId] IN [
  ['PER-001','PRY-001'],['PER-002','PRY-001'],['PER-005','PRY-001'],
  ['PER-003','PRY-002'],['PER-004','PRY-002'],['PER-006','PRY-002']]
MERGE (u)-[:PARTICIPA_EN]->(p);

MATCH (v:VersionDocumento), (d:Documento)
WHERE [v.versionId,d.documentoId] IN [['VER-001','DOC-001'],['VER-002','DOC-002'],['VER-003','DOC-003']]
MERGE (v)-[:VERSION_DE]->(d);

MATCH (d:Documento), (p:Proyecto)
WHERE [d.documentoId,p.proyectoId] IN [['DOC-001','PRY-001'],['DOC-002','PRY-002'],['DOC-003','PRY-001']]
MERGE (d)-[:DOCUMENTA]->(p);

MATCH (c:Conocimiento), (d:Documento)
WHERE [c.conocimientoId,d.documentoId] IN [['CON-001','DOC-001'],['CON-002','DOC-002'],['CON-003','DOC-003']]
MERGE (c)-[:RESPALDADO_POR]->(d);

MATCH (u:Persona), (d:Documento)
WHERE [u.personaId,d.documentoId] IN [['PER-005','DOC-001'],['PER-006','DOC-002'],['PER-002','DOC-003']]
MERGE (u)-[:PROPIETARIO_DE]->(d);

MATCH (r:Repositorio), (p:Proyecto)
WHERE [r.repositorioId,p.proyectoId] IN [['REP-001','PRY-001'],['REP-002','PRY-002']]
MERGE (r)-[:PERTENECE_A_PROYECTO]->(p);

MATCH (r:Repositorio), (c:Componente)
WHERE [r.repositorioId,c.componenteId] IN [['REP-001','CMP-001'],['REP-001','CMP-003'],['REP-002','CMP-002']]
MERGE (r)-[:CONTIENE]->(c);

MATCH (s:Microservicio), (a:API)
WHERE [s.servicioId,a.apiId] IN [['SRV-001','API-001'],['SRV-002','API-002'],['SRV-003','API-003']]
MERGE (s)-[:EXPONE]->(a);

MATCH (c:Componente), (s:Microservicio)
WHERE [c.componenteId,s.servicioId] IN [['CMP-001','SRV-001'],['CMP-002','SRV-002'],['CMP-003','SRV-003']]
MERGE (c)-[:IMPLEMENTA]->(s);

MATCH (d:Decision), (p:Proyecto)
WHERE [d.decisionId,p.proyectoId] IN [['DEC-001','PRY-002'],['DEC-002','PRY-001']]
MERGE (d)-[:AFECTA]->(p);
