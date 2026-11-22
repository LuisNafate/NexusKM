// NexusKM 08 - consultas de demostración.

// Q1. Proyectos con líder y departamento propietario (3 entidades).
MATCH (lider:Persona)-[:LIDERA]->(p:Proyecto)-[:PROPIEDAD_DE]->(d:Departamento)
RETURN p.codigo AS proyecto, lider.nombre AS lider, d.nombre AS departamento
ORDER BY proyecto;

// Q2. Documentos vigentes, propietario y proyecto (4 entidades contando versión).
MATCH (u:Persona)-[:PROPIETARIO_DE]->(d:Documento)<-[:VERSION_DE]-(v:VersionDocumento)
MATCH (d)-[:DOCUMENTA]->(p:Proyecto)
WHERE d.estado='PUBLICADO' AND coalesce(d.activo,true)
  AND v.estado='VIGENTE' AND v.fechaVencimiento > datetime()
RETURN d.titulo AS documento, v.numero AS version, v.estado AS estado,
       u.nombre AS propietario, p.nombre AS proyecto, v.fechaVencimiento AS vence
ORDER BY vence;

// Q3. Impacto de una API: consumidor, dependencia, componente y proyecto (5+ entidades).
MATCH (api:API {apiId:'API-002'})<-[:HACIA]-(rd:RegistroDependencia)-[:DESDE]->(consumidor:Microservicio)
OPTIONAL MATCH (comp:Componente)-[:IMPLEMENTA]->(consumidor)
OPTIONAL MATCH (repo:Repositorio)-[:CONTIENE]->(comp)
OPTIONAL MATCH (repo)-[:PERTENECE_A_PROYECTO]->(p:Proyecto)
RETURN api.nombre AS api, rd.criticidad AS criticidad, consumidor.nombre AS consumidor,
       collect(DISTINCT comp.nombre) AS componentes,
       collect(DISTINCT p.nombre) AS proyectos;

// Q4. Solicitudes con conteo de aprobaciones técnicas distintas.
MATCH (s:SolicitudCambio)
OPTIONAL MATCH (a:Aprobacion {tipo:'TECNICA', decision:'APROBADA'})-[:APRUEBA_SOLICITUD]->(s)
OPTIONAL MATCH (a)-[:EMITIDA_POR]->(revisor:Persona)
RETURN s.solicitudId AS solicitud, s.estado AS estado,
       count(DISTINCT revisor) AS revisoresTecnicos,
       collect(DISTINCT revisor.nombre) AS nombres;

// Q5. Excepciones vigentes, vencidas o próximas a vencer.
MATCH (e:ExcepcionEmergencia)
RETURN e.excepcionId AS excepcion, e.criticidad AS criticidad, e.fechaLimite AS limite,
       CASE WHEN e.estado='CERRADA' THEN 'CERRADA'
            WHEN e.fechaLimite IS NULL THEN 'FECHA_FALTANTE'
            WHEN e.fechaLimite < datetime() THEN 'VENCIDA'
            WHEN e.fechaLimite < datetime() + duration({hours:24}) THEN 'PROXIMA_A_VENCER'
            ELSE e.estado END AS estadoCalculado;

// Q6. Trazabilidad de auditoría por entidad.
MATCH (e:EventoAuditoria)
OPTIONAL MATCH (e)-[:EJECUTADO_POR]->(p:Persona)
RETURN e.fecha AS fecha, e.tipo AS tipo, e.entidad AS entidad,
       e.entidadId AS id, coalesce(p.nombre,'SISTEMA') AS actor
ORDER BY fecha;

// Q7. Sincronizaciones con conflicto y elemento afectado.
MATCH (s:Sincronizacion {estado:'CONFLICTO'})-[:DESDE_ORIGEN]->(o:SistemaOrigen)
OPTIONAL MATCH (s)-[:ACTUALIZA]->(x)
RETURN s.sincronizacionId AS sincronizacion, o.nombre AS origen,
       labels(x) AS tipoAfectado, coalesce(x.titulo,x.nombre) AS afectado;

// Q8. Autorizaciones representadas para una persona y clasificación.
MATCH (p:Persona {personaId:'PER-002'})-[:TIENE_ROL]->(r:Rol)-[:HABILITA]->(pol:PoliticaAcceso)
RETURN p.nombre AS persona, r.nombre AS rol, pol.clasificacion AS clasificacion,
       collect(pol.accion) AS acciones;

// Q9. Conteo general para evidencia de carga.
MATCH (n)
RETURN labels(n)[0] AS etiqueta, count(*) AS cantidad
ORDER BY etiqueta;
