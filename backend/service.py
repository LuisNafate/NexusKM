import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4

from psycopg.types.json import Jsonb

from backend.errors import DomainError
from backend.repositories.document import validate_content
from backend.repositories.relational import audit, connection
from backend.synchronization import enqueue, pending_count, process_pending


def new_id(prefix):
    return prefix + "-" + uuid4().hex[:16].upper()


def can_read(person, document):
    return (
        document["classification"] == "INTERNO"
        or document["owner_id"] == person["person_id"]
        or person["role"] in ("ADMIN", "SEGURIDAD", "TECNICO")
    )


def require_owner(person, document):
    if person["person_id"] != document["owner_id"] and person["role"] != "ADMIN":
        raise DomainError(403, "Esta operación corresponde al propietario documental.")


def locked_document(conn, document_id):
    document = conn.execute(
        "SELECT * FROM documents WHERE document_id=%s AND active FOR UPDATE", (document_id,)
    ).fetchone()
    if not document:
        raise DomainError(404, "Documento inexistente o dado de baja.")
    if conn.execute(
        "SELECT 1 FROM outbox WHERE document_id=%s AND state='PENDIENTE'", (document_id,)
    ).fetchone():
        raise DomainError(409, "El documento tiene una sincronización pendiente. Reintenta la sincronización.")
    return document


def check_revision(actual, expected):
    if actual != expected:
        raise DomainError(409, "Otra operación modificó el registro. Recarga antes de guardar.")


def future_expiration(value):
    if datetime.fromisoformat(value) <= datetime.now(timezone.utc):
        raise DomainError(422, "La fecha de vencimiento debe estar en el futuro.")


def content_payload(version_id, document_id, kind, revision, content):
    validate_content(kind, content)
    return {
        "_id": version_id,
        "documentId": document_id,
        "kind": kind,
        "revision": revision,
        "content": content,
    }


class NexusService:
    def __init__(self, documents, graph):
        self.documents = documents
        self.graph = graph

    def command(self, person, operation_id, action, body, handler):
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        request_hash = hashlib.sha256(canonical.encode()).hexdigest()
        with connection() as conn:
            conn.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (str(operation_id),))
            previous = conn.execute(
                "SELECT * FROM operations WHERE operation_id=%s", (operation_id,)
            ).fetchone()
            if previous:
                same_command = (
                    previous["actor_id"] == person["person_id"]
                    and previous["action"] == action
                    and previous["request_hash"] == request_hash
                )
                if not same_command:
                    raise DomainError(409, "Idempotency-Key ya identifica otra operación.")
                result = dict(previous["response"])
                result["replayed"] = True
            else:
                result = handler(conn, body)
                conn.execute(
                    """INSERT INTO operations(operation_id,actor_id,action,request_hash,response)
                       VALUES (%s,%s,%s,%s,%s)""",
                    (operation_id, person["person_id"], action, request_hash, Jsonb(result)),
                )
                result["replayed"] = False
        synchronization = process_pending(self.documents, self.graph)
        return {"operation_id": str(operation_id), **result, "synchronization": synchronization}

    def list_documents(self, person):
        with connection() as conn:
            rows = conn.execute(
                """SELECT d.*,p.name AS project,owner.name AS owner,
                   (SELECT count(*) FROM versions v WHERE v.document_id=d.document_id) AS version_count,
                   EXISTS(SELECT 1 FROM outbox o WHERE o.document_id=d.document_id AND o.state='PENDIENTE') AS sync_pending
                   FROM documents d JOIN projects p USING(project_id)
                   JOIN people owner ON owner.person_id=d.owner_id WHERE d.active ORDER BY d.title"""
            ).fetchall()
        return [row for row in rows if can_read(person, row)]

    def document_detail(self, person, document_id):
        with connection() as conn:
            document = conn.execute(
                "SELECT * FROM documents WHERE document_id=%s AND active", (document_id,)
            ).fetchone()
            if not document:
                raise DomainError(404, "Documento inexistente o dado de baja.")
            if not can_read(person, document):
                raise DomainError(403, "Tu rol no permite consultar este documento restringido.")
            versions = conn.execute(
                "SELECT * FROM versions WHERE document_id=%s ORDER BY version_id", (document_id,)
            ).fetchall()
        for version in versions:
            record = self.documents.get(version["version_id"])
            version["content"] = record["content"] if record else None
            version["content_ready"] = bool(record and record["revision"] == version["content_revision"])
            version["expired"] = version["expires_at"] <= datetime.now(timezone.utc)
        return {"document": document, "versions": versions, "sync_pending": pending_count(document_id) > 0}

    def create_document(self, person, operation_id, body):
        def create(conn, data):
            if data["owner_id"] != person["person_id"] and person["role"] != "ADMIN":
                raise DomainError(403, "Puedes crear documentos propios. Administración puede asignar otro propietario.")
            future_expiration(data["expires_at"])
            document_id = new_id("DOC")
            version_id = new_id("VER")
            payload = content_payload(version_id, document_id, data["kind"], 1, data["content"])
            conn.execute(
                """INSERT INTO documents(document_id,title,kind,classification,owner_id,project_id)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (document_id, data["title"], data["kind"], data["classification"], data["owner_id"], data["project_id"]),
            )
            conn.execute(
                """INSERT INTO versions(version_id,document_id,number,state,expires_at)
                   VALUES (%s,%s,%s,'BORRADOR',%s)""",
                (version_id, document_id, data["number"], data["expires_at"]),
            )
            enqueue(conn, document_id, payload)
            audit(conn, person["person_id"], "DOCUMENTO_CREADO", document_id)
            return {"document_id": document_id, "version_id": version_id, "revision": 1}
        return self.command(person, operation_id, "CREATE_DOCUMENT", body, create)

    def rename_document(self, person, operation_id, document_id, body):
        def rename(conn, data):
            document = locked_document(conn, document_id)
            require_owner(person, document)
            check_revision(document["revision"], data["expected_revision"])
            conn.execute(
                "UPDATE documents SET title=%s,revision=revision+1 WHERE document_id=%s",
                (data["title"], document_id),
            )
            enqueue(conn, document_id)
            audit(conn, person["person_id"], "DOCUMENTO_ACTUALIZADO", document_id)
            return {"document_id": document_id, "revision": document["revision"] + 1}
        return self.command(person, operation_id, "RENAME:" + document_id, body, rename)

    def create_version(self, person, operation_id, document_id, body):
        def create(conn, data):
            document = locked_document(conn, document_id)
            require_owner(person, document)
            future_expiration(data["expires_at"])
            version_id = new_id("VER")
            payload = content_payload(version_id, document_id, document["kind"], 1, data["content"])
            conn.execute(
                """INSERT INTO versions(version_id,document_id,number,state,expires_at)
                   VALUES (%s,%s,%s,'BORRADOR',%s)""",
                (version_id, document_id, data["number"], data["expires_at"]),
            )
            enqueue(conn, document_id, payload)
            audit(conn, person["person_id"], "VERSION_CREADA", version_id)
            return {"document_id": document_id, "version_id": version_id, "revision": 1}
        return self.command(person, operation_id, "CREATE_VERSION:" + document_id, body, create)

    def edit_content(self, person, operation_id, version_id, body):
        def edit(conn, data):
            version = conn.execute("SELECT * FROM versions WHERE version_id=%s", (version_id,)).fetchone()
            if not version:
                raise DomainError(404, "Versión inexistente.")
            document = locked_document(conn, version["document_id"])
            require_owner(person, document)
            version = conn.execute("SELECT * FROM versions WHERE version_id=%s FOR UPDATE", (version_id,)).fetchone()
            if version["state"] != "BORRADOR":
                raise DomainError(409, "El contenido se modifica mientras la versión está en borrador.")
            check_revision(version["content_revision"], data["expected_revision"])
            revision = version["content_revision"] + 1
            payload = content_payload(version_id, document["document_id"], document["kind"], revision, data["content"])
            conn.execute("UPDATE versions SET content_revision=%s WHERE version_id=%s", (revision, version_id))
            enqueue(conn, document["document_id"], payload)
            audit(conn, person["person_id"], "CONTENIDO_ACTUALIZADO", version_id)
            return {"document_id": document["document_id"], "version_id": version_id, "revision": revision}
        return self.command(person, operation_id, "EDIT_CONTENT:" + version_id, body, edit)

    def delete_document(self, person, operation_id, document_id, expected_revision):
        def delete(conn, data):
            document = locked_document(conn, document_id)
            require_owner(person, document)
            check_revision(document["revision"], data["expected_revision"])
            if conn.execute(
                """SELECT 1 FROM versions v LEFT JOIN change_requests r USING(version_id)
                   WHERE v.document_id=%s AND (v.state='VIGENTE' OR r.state IN ('PENDIENTE','APROBADA'))""",
                (document_id,),
            ).fetchone():
                raise DomainError(409, "La baja requiere un documento sin publicación vigente ni solicitudes abiertas.")
            conn.execute("UPDATE documents SET active=false,revision=revision+1 WHERE document_id=%s", (document_id,))
            conn.execute("UPDATE versions SET state='RETIRADA' WHERE document_id=%s", (document_id,))
            enqueue(conn, document_id, action="DELETE")
            audit(conn, person["person_id"], "DOCUMENTO_DADO_DE_BAJA", document_id)
            return {"document_id": document_id, "state": "INACTIVO"}
        return self.command(
            person, operation_id, "DELETE:" + document_id,
            {"expected_revision": expected_revision}, delete,
        )

    def list_requests(self, person):
        with connection() as conn:
            rows = conn.execute(
                """SELECT r.*,d.title,d.document_id,d.owner_id,d.classification,
                   v.number AS version_number, p.name AS requester
                   FROM change_requests r JOIN versions v USING(version_id)
                   JOIN documents d USING(document_id) JOIN people p ON p.person_id=r.requester_id
                   WHERE d.active ORDER BY r.created_at DESC"""
            ).fetchall()
            for row in rows:
                row["approvals"] = conn.execute(
                    """SELECT a.approval_id,a.kind,a.reviewer_id,p.name AS reviewer
                       FROM approvals a JOIN people p ON p.person_id=a.reviewer_id
                       WHERE a.request_id=%s ORDER BY a.created_at""",
                    (row["request_id"],),
                ).fetchall()
        return [row for row in rows if can_read(person, row)]

    def create_request(self, person, operation_id, body):
        def create(conn, data):
            version = conn.execute("SELECT * FROM versions WHERE version_id=%s", (data["version_id"],)).fetchone()
            if not version:
                raise DomainError(404, "Versión inexistente.")
            document = locked_document(conn, version["document_id"])
            require_owner(person, document)
            version = conn.execute("SELECT * FROM versions WHERE version_id=%s FOR UPDATE", (data["version_id"],)).fetchone()
            if version["state"] != "BORRADOR":
                raise DomainError(409, "La solicitud requiere una versión en borrador.")
            future_expiration(version["expires_at"].isoformat())
            request_id = new_id("SOL")
            conn.execute(
                "INSERT INTO change_requests(request_id,version_id,requester_id) VALUES (%s,%s,%s)",
                (request_id, data["version_id"], person["person_id"]),
            )
            conn.execute("UPDATE versions SET state='EN_REVISION' WHERE version_id=%s", (data["version_id"],))
            enqueue(conn, document["document_id"])
            audit(conn, person["person_id"], "SOLICITUD_CREADA", request_id)
            return {"request_id": request_id, "state": "PENDIENTE"}
        return self.command(person, operation_id, "CREATE_REQUEST", body, create)

    def request_context(self, conn, request_id):
        row = conn.execute(
            """SELECT r.*,v.document_id FROM change_requests r JOIN versions v USING(version_id)
               WHERE r.request_id=%s""", (request_id,)
        ).fetchone()
        if not row:
            raise DomainError(404, "Solicitud inexistente.")
        document = locked_document(conn, row["document_id"])
        request = conn.execute(
            "SELECT * FROM change_requests WHERE request_id=%s FOR UPDATE", (request_id,)
        ).fetchone()
        return request, document

    def approval_requirements_met(self, conn, request, document):
        approvals = conn.execute(
            """SELECT a.*,p.role,p.active FROM approvals a JOIN people p ON p.person_id=a.reviewer_id
               WHERE a.request_id=%s""", (request["request_id"],)
        ).fetchall()
        technical = {
            a["reviewer_id"] for a in approvals
            if a["kind"] == "TECNICA" and a["role"] == "TECNICO" and a["active"]
            and a["reviewer_id"] != request["requester_id"]
        }
        owner = any(a["kind"] == "PROPIETARIO" and a["reviewer_id"] == document["owner_id"] and a["active"] for a in approvals)
        security = document["classification"] == "INTERNO" or any(
            a["kind"] == "SEGURIDAD" and a["role"] == "SEGURIDAD" and a["active"] for a in approvals
        )
        return len(technical) >= 2 and owner and security

    def approve(self, person, operation_id, request_id, body):
        def approve(conn, data):
            request, document = self.request_context(conn, request_id)
            if request["state"] not in ("PENDIENTE", "APROBADA"):
                raise DomainError(409, "Esta solicitud está cerrada.")
            kind = data["kind"]
            permitted = {
                "TECNICA": person["role"] == "TECNICO" and person["person_id"] != request["requester_id"],
                "SEGURIDAD": person["role"] == "SEGURIDAD",
                "PROPIETARIO": person["person_id"] == document["owner_id"],
            }[kind]
            if not permitted:
                raise DomainError(403, "Tu identidad o rol no permite emitir esta aprobación.")
            conn.execute(
                """INSERT INTO approvals(approval_id,request_id,reviewer_id,kind)
                   VALUES (%s,%s,%s,%s)""",
                (new_id("APR"), request_id, person["person_id"], kind),
            )
            state = "APROBADA" if self.approval_requirements_met(conn, request, document) else "PENDIENTE"
            conn.execute("UPDATE change_requests SET state=%s WHERE request_id=%s", (state, request_id))
            enqueue(conn, document["document_id"])
            audit(conn, person["person_id"], "APROBACION_REGISTRADA", request_id, {"kind": kind})
            return {"request_id": request_id, "state": state}
        return self.command(person, operation_id, "APPROVE:" + request_id, body, approve)

    def publish(self, person, operation_id, request_id):
        def publish(conn, data):
            request, document = self.request_context(conn, request_id)
            require_owner(person, document)
            if request["state"] != "APROBADA" or not self.approval_requirements_met(conn, request, document):
                raise DomainError(409, "La publicación requiere dos revisores técnicos y las aprobaciones aplicables.")
            version = conn.execute("SELECT * FROM versions WHERE version_id=%s", (request["version_id"],)).fetchone()
            future_expiration(version["expires_at"].isoformat())
            content = self.documents.get(version["version_id"])
            if not content or content["revision"] != version["content_revision"]:
                raise DomainError(409, "El contenido de la versión aún no está sincronizado.")
            conn.execute(
                "UPDATE versions SET state='RETIRADA' WHERE document_id=%s AND state='VIGENTE'",
                (document["document_id"],),
            )
            conn.execute(
                "UPDATE versions SET state='VIGENTE',published_at=now() WHERE version_id=%s",
                (version["version_id"],),
            )
            conn.execute("UPDATE change_requests SET state='PUBLICADA' WHERE request_id=%s", (request_id,))
            enqueue(conn, document["document_id"])
            audit(conn, person["person_id"], "VERSION_PUBLICADA", version["version_id"])
            return {"request_id": request_id, "version_id": version["version_id"], "state": "PUBLICADA"}
        return self.command(person, operation_id, "PUBLISH:" + request_id, {}, publish)

    def impact(self, person, api_id):
        paths = self.graph.impact(api_id)
        if not paths:
            raise DomainError(404, "API inexistente.")
        project_ids = sorted({path["project_id"] for path in paths if path["project_id"]})
        documents = []
        sources = ["Neo4j", "PostgreSQL"]
        with connection() as conn:
            projects = conn.execute(
                """SELECT p.*,u.name AS leader FROM projects p JOIN people u ON u.person_id=p.leader_id
                   WHERE p.project_id=ANY(%s) AND p.active""", (project_ids,)
            ).fetchall()
            rows = conn.execute(
                """SELECT d.*,v.version_id,v.number,v.content_revision,v.expires_at
                   FROM documents d JOIN versions v USING(document_id)
                   WHERE d.project_id=ANY(%s) AND d.active AND v.state='VIGENTE' AND v.expires_at>now()""",
                (project_ids,),
            ).fetchall()
        for row in rows:
            if can_read(person, row):
                content = self.documents.get(row["version_id"])
                if "MongoDB" not in sources:
                    sources.append("MongoDB")
                row["content"] = content["content"] if content else None
                row["content_ready"] = bool(content and content["revision"] == row["content_revision"])
                documents.append(row)
        return {
            "api_id": api_id, "api_name": paths[0]["api_name"], "paths": paths,
            "projects": projects, "documents": documents,
            "sources": sources,
            "synchronization_pending": pending_count(),
        }
