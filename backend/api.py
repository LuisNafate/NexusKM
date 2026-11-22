from uuid import UUID

import psycopg
from fastapi import APIRouter, Depends, Header, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from backend.auth import check_password, current_person, issue_token
from backend.errors import DomainError
from backend.models import (
    ApprovalInput, ContentUpdate, DocumentInput, Login, RenameDocument, RequestInput, VersionInput,
)
from backend.repositories.relational import connection
from backend.synchronization import process_pending

router = APIRouter(prefix="/api")


def service(request: Request):
    return request.app.state.service


def command_response(result, created=False):
    status = 202 if result["synchronization"]["pending"] else (201 if created else 200)
    return JSONResponse(jsonable_encoder(result), status_code=status)


@router.get("/health", tags=["Estado"])
def health(request: Request):
    states = {}
    try:
        with connection() as conn:
            conn.execute("SELECT 1")
        states["postgresql"] = True
    except psycopg.Error:
        states["postgresql"] = False
    for name, repository in [
        ("mongodb", request.app.state.service.documents),
        ("neo4j", request.app.state.service.graph),
    ]:
        try:
            states[name] = repository.ping()
        except Exception:
            states[name] = False
    healthy = all(states.values())
    return JSONResponse({"healthy": healthy, "databases": states}, status_code=200 if healthy else 503)


@router.post("/auth/login", tags=["Autenticación"])
def login(data: Login):
    with connection() as conn:
        person = conn.execute(
            "SELECT * FROM people WHERE (person_id=%s OR email=%s) AND active",
            (data.person_id, data.person_id),
        ).fetchone()
    if not person or not check_password(data.password, person["password_hash"]):
        raise DomainError(401, "Usuario o contraseña incorrectos.")
    return {
        "access_token": issue_token(person["person_id"]),
        "token_type": "bearer",
        "expires_in": 3600,
        "person": {key: person[key] for key in ("person_id", "name", "role", "department_id")},
    }


@router.get("/me", tags=["Autenticación"])
def me(person=Depends(current_person)):
    return person


@router.get("/catalog", tags=["Catálogo"])
def catalog(nexus=Depends(service), person=Depends(current_person)):
    with connection() as conn:
        projects = conn.execute("SELECT * FROM projects WHERE active ORDER BY code").fetchall()
        people = conn.execute("SELECT person_id,name,role FROM people WHERE active ORDER BY name").fetchall()
    apis = nexus.graph.query("MATCH (a:API) RETURN a.apiId AS api_id,a.nombre AS name ORDER BY name")
    return {"projects": projects, "people": people, "apis": apis}


@router.get("/documents", tags=["Documentos"])
def documents(nexus=Depends(service), person=Depends(current_person)):
    return nexus.list_documents(person)


@router.get("/documents/{document_id}", tags=["Documentos"])
def document_detail(document_id: str, nexus=Depends(service), person=Depends(current_person)):
    return nexus.document_detail(person, document_id)


@router.post("/documents", tags=["Documentos"])
def create_document(data: DocumentInput, idempotency_key: UUID = Header(),
                    nexus=Depends(service), person=Depends(current_person)):
    return command_response(
        nexus.create_document(person, idempotency_key, data.model_dump(mode="json", exclude_none=True)), True,
    )


@router.patch("/documents/{document_id}", tags=["Documentos"])
def rename_document(document_id: str, data: RenameDocument, idempotency_key: UUID = Header(),
                    nexus=Depends(service), person=Depends(current_person)):
    return command_response(nexus.rename_document(
        person, idempotency_key, document_id, data.model_dump(mode="json"),
    ))


@router.delete("/documents/{document_id}", tags=["Documentos"])
def delete_document(document_id: str, expected_revision: int = Query(ge=1),
                    idempotency_key: UUID = Header(), nexus=Depends(service), person=Depends(current_person)):
    return command_response(nexus.delete_document(person, idempotency_key, document_id, expected_revision))


@router.post("/documents/{document_id}/versions", tags=["Versiones"])
def create_version(document_id: str, data: VersionInput, idempotency_key: UUID = Header(),
                   nexus=Depends(service), person=Depends(current_person)):
    return command_response(nexus.create_version(
        person, idempotency_key, document_id, data.model_dump(mode="json", exclude_none=True),
    ), True)


@router.put("/versions/{version_id}/content", tags=["Versiones"])
def edit_content(version_id: str, data: ContentUpdate, idempotency_key: UUID = Header(),
                 nexus=Depends(service), person=Depends(current_person)):
    return command_response(nexus.edit_content(
        person, idempotency_key, version_id, data.model_dump(mode="json", exclude_none=True),
    ))


@router.get("/requests", tags=["Aprobaciones"])
def requests(nexus=Depends(service), person=Depends(current_person)):
    return nexus.list_requests(person)


@router.post("/requests", tags=["Aprobaciones"])
def create_request(data: RequestInput, idempotency_key: UUID = Header(),
                   nexus=Depends(service), person=Depends(current_person)):
    return command_response(nexus.create_request(person, idempotency_key, data.model_dump()), True)


@router.post("/requests/{request_id}/approvals", tags=["Aprobaciones"])
def approve(request_id: str, data: ApprovalInput, idempotency_key: UUID = Header(),
            nexus=Depends(service), person=Depends(current_person)):
    return command_response(nexus.approve(person, idempotency_key, request_id, data.model_dump()))


@router.post("/requests/{request_id}/publish", tags=["Aprobaciones"])
def publish(request_id: str, idempotency_key: UUID = Header(),
            nexus=Depends(service), person=Depends(current_person)):
    return command_response(nexus.publish(person, idempotency_key, request_id))


@router.get("/impact/{api_id}", tags=["Impacto"])
def impact(api_id: str, nexus=Depends(service), person=Depends(current_person)):
    return nexus.impact(person, api_id)


@router.get("/audit", tags=["Auditoría"])
def audit_events(person=Depends(current_person)):
    with connection() as conn:
        return conn.execute(
            """SELECT e.*,p.name AS actor FROM audit_events e LEFT JOIN people p ON p.person_id=e.actor_id
               WHERE (%s OR e.actor_id=%s) ORDER BY e.event_id DESC LIMIT 100""",
            (person["role"] in ("ADMIN", "SEGURIDAD"), person["person_id"]),
        ).fetchall()


@router.get("/synchronization", tags=["Sincronización"])
def synchronization(person=Depends(current_person)):
    if person["role"] != "ADMIN":
        raise DomainError(403, "Esta vista corresponde a administración.")
    with connection() as conn:
        return conn.execute(
            """SELECT event_id,document_id,action,state,attempts,last_error,created_at,completed_at
               FROM outbox ORDER BY event_id DESC LIMIT 100"""
        ).fetchall()


@router.post("/synchronization/retry", tags=["Sincronización"])
def retry(nexus=Depends(service), person=Depends(current_person)):
    if person["role"] != "ADMIN":
        raise DomainError(403, "El reintento corresponde a administración.")
    return process_pending(nexus.documents, nexus.graph, limit=100)
