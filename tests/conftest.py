from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.repositories.document import DocumentRepository
from backend.repositories.graph import GraphRepository
from backend.repositories.relational import connection
from backend.service import NexusService
from backend.settings import required
from scripts.bootstrap import bootstrap


@pytest.fixture(scope="session")
def client():
    bootstrap()
    app.state.service = NexusService(DocumentRepository(), GraphRepository())
    client = TestClient(app)
    yield client
    client.close()
    app.state.service.documents.close()
    app.state.service.graph.close()


@pytest.fixture(scope="session")
def headers(client):
    result = {}
    for number in range(1, 7):
        person_id = f"PER-{number:03d}"
        login = client.post("/api/auth/login", json={
            "person_id": person_id, "password": required("DEMO_PASSWORD"),
        })
        assert login.status_code == 200
        result[person_id] = {"Authorization": "Bearer " + login.json()["access_token"]}
    return result


@pytest.fixture(scope="session")
def created_documents(client):
    created = []
    yield created
    if not created:
        return
    with connection() as conn:
        versions = [row["version_id"] for row in conn.execute(
            "SELECT version_id FROM versions WHERE document_id=ANY(%s)", (created,)
        ).fetchall()]
        requests = [row["request_id"] for row in conn.execute(
            "SELECT request_id FROM change_requests WHERE version_id=ANY(%s)", (versions,)
        ).fetchall()]
        approvals = [row["approval_id"] for row in conn.execute(
            "SELECT approval_id FROM approvals WHERE request_id=ANY(%s)", (requests,)
        ).fetchall()]
        entities = created + versions + requests
        conn.execute("DELETE FROM operations WHERE response->>'document_id'=ANY(%s) OR response->>'version_id'=ANY(%s) OR response->>'request_id'=ANY(%s)", (created, versions, requests))
        conn.execute("DELETE FROM audit_events WHERE entity_id=ANY(%s)", (entities,))
        conn.execute("DELETE FROM outbox WHERE document_id=ANY(%s)", (created,))
        conn.execute("DELETE FROM approvals WHERE request_id=ANY(%s)", (requests,))
        conn.execute("DELETE FROM change_requests WHERE version_id=ANY(%s)", (versions,))
        conn.execute("DELETE FROM versions WHERE document_id=ANY(%s)", (created,))
        conn.execute("DELETE FROM documents WHERE document_id=ANY(%s)", (created,))
    client.app.state.service.documents.collection.delete_many({"documentId": {"$in": created}})
    client.app.state.service.graph.query(
        """MATCH (n) WHERE n.documentoId IN $ids OR n.versionId IN $ids
           OR n.solicitudId IN $ids OR n.aprobacionId IN $ids DETACH DELETE n""",
        ids=entities + approvals,
    )


@pytest.fixture
def create_document(client, headers, created_documents):
    def create(person="PER-005", **changes):
        payload = {
            "title": "Prueba de integración " + uuid4().hex[:8],
            "kind": "RUNBOOK", "classification": "INTERNO",
            "owner_id": person, "project_id": "PRY-001", "number": "1.0",
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "content": {
                "summary": "Contenido de prueba para verificar el flujo integrado.",
                "sections": [{"heading": "Alcance", "body": "Esta versión verifica las reglas del proyecto."}],
                "steps": [{"title": "Verificar", "instruction": "Comprobar el resultado antes de confirmar."}],
            },
        }
        payload.update(changes)
        key = str(uuid4())
        response = client.post("/api/documents", json=payload, headers={
            **headers[person], "Idempotency-Key": key,
        })
        assert response.status_code in (201, 202), response.text
        record = response.json()
        created_documents.append(record["document_id"])
        return record, payload, key
    return create


@pytest.fixture
def write(client, headers):
    def perform(path, person="PER-005", body=None, method="POST", key=None):
        return client.request(method, "/api" + path, json=body, headers={
            **headers[person], "Idempotency-Key": key or str(uuid4()),
        })
    return perform
