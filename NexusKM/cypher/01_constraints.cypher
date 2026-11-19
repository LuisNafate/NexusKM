// NexusKM 01 - restricciones e índices. Neo4j 5.x.
CREATE CONSTRAINT departamento_id IF NOT EXISTS FOR (n:Departamento) REQUIRE n.departamentoId IS UNIQUE;
CREATE CONSTRAINT persona_id IF NOT EXISTS FOR (n:Persona) REQUIRE n.personaId IS UNIQUE;
CREATE CONSTRAINT persona_correo IF NOT EXISTS FOR (n:Persona) REQUIRE n.correo IS UNIQUE;
CREATE CONSTRAINT rol_id IF NOT EXISTS FOR (n:Rol) REQUIRE n.rolId IS UNIQUE;
CREATE CONSTRAINT proyecto_id IF NOT EXISTS FOR (n:Proyecto) REQUIRE n.proyectoId IS UNIQUE;
CREATE CONSTRAINT conocimiento_id IF NOT EXISTS FOR (n:Conocimiento) REQUIRE n.conocimientoId IS UNIQUE;
CREATE CONSTRAINT documento_id IF NOT EXISTS FOR (n:Documento) REQUIRE n.documentoId IS UNIQUE;
CREATE CONSTRAINT version_id IF NOT EXISTS FOR (n:VersionDocumento) REQUIRE n.versionId IS UNIQUE;
CREATE CONSTRAINT decision_id IF NOT EXISTS FOR (n:Decision) REQUIRE n.decisionId IS UNIQUE;
CREATE CONSTRAINT repositorio_id IF NOT EXISTS FOR (n:Repositorio) REQUIRE n.repositorioId IS UNIQUE;
CREATE CONSTRAINT componente_id IF NOT EXISTS FOR (n:Componente) REQUIRE n.componenteId IS UNIQUE;
CREATE CONSTRAINT servicio_id IF NOT EXISTS FOR (n:Microservicio) REQUIRE n.servicioId IS UNIQUE;
CREATE CONSTRAINT api_id IF NOT EXISTS FOR (n:API) REQUIRE n.apiId IS UNIQUE;
CREATE CONSTRAINT dependencia_id IF NOT EXISTS FOR (n:RegistroDependencia) REQUIRE n.dependenciaId IS UNIQUE;
CREATE CONSTRAINT solicitud_id IF NOT EXISTS FOR (n:SolicitudCambio) REQUIRE n.solicitudId IS UNIQUE;
CREATE CONSTRAINT aprobacion_id IF NOT EXISTS FOR (n:Aprobacion) REQUIRE n.aprobacionId IS UNIQUE;
CREATE CONSTRAINT excepcion_id IF NOT EXISTS FOR (n:ExcepcionEmergencia) REQUIRE n.excepcionId IS UNIQUE;
CREATE CONSTRAINT delegacion_id IF NOT EXISTS FOR (n:Delegacion) REQUIRE n.delegacionId IS UNIQUE;
CREATE CONSTRAINT conflicto_id IF NOT EXISTS FOR (n:Conflicto) REQUIRE n.conflictoId IS UNIQUE;
CREATE CONSTRAINT escalamiento_id IF NOT EXISTS FOR (n:Escalamiento) REQUIRE n.escalamientoId IS UNIQUE;
CREATE CONSTRAINT evento_id IF NOT EXISTS FOR (n:EventoAuditoria) REQUIRE n.eventoId IS UNIQUE;
CREATE CONSTRAINT origen_id IF NOT EXISTS FOR (n:SistemaOrigen) REQUIRE n.origenId IS UNIQUE;
CREATE CONSTRAINT sincronizacion_id IF NOT EXISTS FOR (n:Sincronizacion) REQUIRE n.sincronizacionId IS UNIQUE;
CREATE CONSTRAINT politica_id IF NOT EXISTS FOR (n:PoliticaAcceso) REQUIRE n.politicaId IS UNIQUE;

CREATE INDEX proyecto_nombre IF NOT EXISTS FOR (n:Proyecto) ON (n.nombre);
CREATE INDEX documento_titulo IF NOT EXISTS FOR (n:Documento) ON (n.titulo);
CREATE INDEX componente_nombre IF NOT EXISTS FOR (n:Componente) ON (n.nombre);
CREATE INDEX dependencia_criticidad IF NOT EXISTS FOR (n:RegistroDependencia) ON (n.criticidad);
CREATE INDEX solicitud_estado IF NOT EXISTS FOR (n:SolicitudCambio) ON (n.estado);
CREATE INDEX evento_fecha IF NOT EXISTS FOR (n:EventoAuditoria) ON (n.fecha);

SHOW CONSTRAINTS YIELD name, type, labelsOrTypes, properties
RETURN name, type, labelsOrTypes, properties ORDER BY name;
