import os

from neo4j import GraphDatabase

from backend.settings import required


class GraphRepository:
    def __init__(self):
        uri = f"bolt://{os.getenv('NEO4J_HOST', '127.0.0.1')}:{os.getenv('NEO4J_BOLT_PORT', '57687')}"
        self.driver = GraphDatabase.driver(
            uri,
            auth=(os.getenv("NEO4J_USER", "neo4j"), required("NEO4J_PASSWORD")),
            connection_timeout=3,
            connection_acquisition_timeout=3,
            max_transaction_retry_time=3,
        )

    def query(self, query, **parameters):
        with self.driver.session(database="neo4j") as session:
            return session.run(query, parameters).data()

    def ping(self):
        self.driver.verify_connectivity()
        return True

    def impact(self, api_id):
        return self.query(
            """
            MATCH (api:API {apiId:$api_id})
            OPTIONAL MATCH (api)<-[:HACIA]-(dependency:RegistroDependencia)-[:DESDE]->(service:Microservicio)
            OPTIONAL MATCH (component:Componente)-[:IMPLEMENTA]->(service)
            OPTIONAL MATCH (repository:Repositorio)-[:CONTIENE]->(component)
            OPTIONAL MATCH (repository)-[:PERTENECE_A_PROYECTO]->(project:Proyecto)
            RETURN api.apiId AS api_id, api.nombre AS api_name,
                dependency.dependenciaId AS dependency_id, dependency.criticidad AS criticality,
                service.nombre AS service, component.nombre AS component,
                repository.nombre AS repository, project.proyectoId AS project_id,
                project.nombre AS project
            ORDER BY project, service, component
            """,
            api_id=api_id,
        )

    def sync_document(self, snapshot):
        def write(tx):
            tx.run(
                """
                MERGE (d:Documento {documentoId:$document_id})
                SET d.titulo=$title, d.tipo=$kind, d.clasificacion=$classification,
                    d.activo=$active, d.estado=$state, d.revision=$revision
                WITH d
                OPTIONAL MATCH (d)-[old:DOCUMENTA]->()
                DELETE old
                WITH DISTINCT d
                OPTIONAL MATCH ()-[old:PROPIETARIO_DE]->(d)
                DELETE old
                WITH DISTINCT d
                MERGE (p:Proyecto {proyectoId:$project_id})
                MERGE (u:Persona {personaId:$owner_id})
                MERGE (d)-[:DOCUMENTA]->(p)
                MERGE (u)-[:PROPIETARIO_DE]->(d)
                """,
                **snapshot["document"],
            ).consume()
            for version in snapshot["versions"]:
                tx.run(
                    """
                    MATCH (d:Documento {documentoId:$document_id})
                    MERGE (v:VersionDocumento {versionId:$version_id})
                    SET v.numero=$number, v.estado=$state,
                        v.fechaVencimiento=datetime($expires_at),
                        v.fechaPublicacion=CASE WHEN $published_at IS NULL THEN null ELSE datetime($published_at) END
                    MERGE (v)-[:VERSION_DE]->(d)
                    """,
                    **version,
                ).consume()
            for request in snapshot["requests"]:
                tx.run(
                    """
                    MATCH (v:VersionDocumento {versionId:$version_id})
                    MERGE (s:SolicitudCambio {solicitudId:$request_id})
                    SET s.estado=$state, s.creadaEn=$created_at,
                        s.titulo='Revisar ' + $version_id
                    MERGE (s)-[:SOBRE]->(v)
                    WITH s
                    MERGE (p:Persona {personaId:$requester_id})
                    MERGE (p)-[:SOLICITA]->(s)
                    """,
                    **request,
                ).consume()
            for approval in snapshot["approvals"]:
                tx.run(
                    """
                    MATCH (s:SolicitudCambio {solicitudId:$request_id})
                    MERGE (a:Aprobacion {aprobacionId:$approval_id})
                    SET a.tipo=$kind, a.decision='APROBADA', a.fecha=$created_at
                    MERGE (p:Persona {personaId:$reviewer_id})
                    MERGE (a)-[:APRUEBA_SOLICITUD]->(s)
                    MERGE (a)-[:EMITIDA_POR]->(p)
                    """,
                    **approval,
                ).consume()

        with self.driver.session(database="neo4j") as session:
            session.execute_write(write)

    def close(self):
        self.driver.close()
