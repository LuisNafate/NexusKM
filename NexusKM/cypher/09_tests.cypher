// NexusKM 09 - pruebas. Las consultas de violación deben devolver cero filas.

// T1. Cada persona tiene exactamente un departamento.
MATCH (p:Persona)
OPTIONAL MATCH (p)-[:PERTENECE_A]->(d:Departamento)
WITH p, count(d) AS cantidad
WHERE cantidad <> 1
RETURN p.personaId AS violacion, cantidad;

// T2. Cada proyecto tiene exactamente un departamento propietario.
MATCH (p:Proyecto)
OPTIONAL MATCH (p)-[:PROPIEDAD_DE]->(d:Departamento)
WITH p, count(d) AS cantidad
WHERE cantidad <> 1
RETURN p.proyectoId AS violacion, cantidad;

// T3. Cada proyecto tiene exactamente un líder.
MATCH (p:Proyecto)
OPTIONAL MATCH (u:Persona)-[:LIDERA]->(p)
WITH p, count(u) AS cantidad
WHERE cantidad <> 1
RETURN p.proyectoId AS violacion, cantidad;

// T4. Una versión pertenece exactamente a un documento.
MATCH (v:VersionDocumento)
OPTIONAL MATCH (v)-[:VERSION_DE]->(d:Documento)
WITH v, count(d) AS cantidad
WHERE cantidad <> 1
RETURN v.versionId AS violacion, cantidad;

// T5. Solicitudes aprobadas requieren dos revisores técnicos distintos.
MATCH (s:SolicitudCambio {estado:'APROBADA'})
OPTIONAL MATCH (a:Aprobacion {tipo:'TECNICA', decision:'APROBADA'})-[:APRUEBA_SOLICITUD]->(s)
OPTIONAL MATCH (a)-[:EMITIDA_POR]->(p:Persona)
WITH s, count(DISTINCT p) AS revisores
WHERE revisores < 2
RETURN s.solicitudId AS violacion, revisores;

// T6. El solicitante no puede aprobar técnicamente su propia solicitud.
MATCH (p:Persona)-[:SOLICITA]->(s:SolicitudCambio)
MATCH (a:Aprobacion {tipo:'TECNICA'})-[:APRUEBA_SOLICITUD]->(s)
MATCH (a)-[:EMITIDA_POR]->(p)
RETURN s.solicitudId AS violacion, p.personaId AS persona;

// T7. Toda dependencia registrada tiene origen y destino.
MATCH (r:RegistroDependencia)
OPTIONAL MATCH (r)-[:DESDE]->(o)
OPTIONAL MATCH (r)-[:HACIA]->(d)
WITH r, count(DISTINCT o) AS origenes, count(DISTINCT d) AS destinos
WHERE origenes <> 1 OR destinos <> 1
RETURN r.dependenciaId AS violacion, origenes, destinos;

// T8. Excepciones críticas respetan el máximo declarado de 48 horas hábiles.
MATCH (e:ExcepcionEmergencia {criticidad:'CRITICA'})
WHERE e.horasHabilesAprobadas > 48 OR e.horasHabilesAprobadas IS NULL
RETURN e.excepcionId AS violacion, e.horasHabilesAprobadas AS horas;

// T9. Documentos publicados tienen al menos una versión vigente.
MATCH (d:Documento {estado:'PUBLICADO'})
WHERE NOT EXISTS { MATCH (:VersionDocumento {estado:'VIGENTE'})-[:VERSION_DE]->(d) }
RETURN d.documentoId AS violacion;

// T10. Resumen positivo esperado.
MATCH (n)
RETURN count(n) AS nodos;
MATCH ()-[r]->()
RETURN count(r) AS relaciones;
