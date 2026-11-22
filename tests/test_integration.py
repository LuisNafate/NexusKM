import copy
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import psycopg
import pytest
from neo4j.exceptions import ConstraintError, ServiceUnavailable
from pymongo.errors import WriteError

from backend.auth import decode_token, issue_token
from backend.errors import DomainError
from backend.repositories.relational import connection
from backend.settings import ROOT
from scripts.bootstrap import statements


def test_connectivity_to_three_real_databases(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["databases"] == {"postgresql": True, "mongodb": True, "neo4j": True}


def test_authentication_required(client):
    assert client.get("/api/documents").status_code == 401


def test_wrong_password_rejected(client):
    assert client.post("/api/auth/login", json={"person_id": "PER-002", "password": "incorrecta"}).status_code == 401


def test_tampered_token_rejected():
    token = issue_token("PER-002")
    with pytest.raises(DomainError):
        decode_token(token + "f")


def test_expired_token_rejected(monkeypatch):
    monkeypatch.setattr("backend.auth.time.time", lambda: 1)
    token = issue_token("PER-002")
    monkeypatch.setattr("backend.auth.time.time", lambda: 10000)
    with pytest.raises(DomainError):
        decode_token(token)


def test_catalog_has_reused_identifiers(client, headers):
    result = client.get("/api/catalog", headers=headers["PER-002"]).json()
    assert len(result["projects"]) == 2
    assert {p["person_id"] for p in result["people"]} == {f"PER-{n:03d}" for n in range(1, 7)}
    assert "API-002" in {api["api_id"] for api in result["apis"]}


def test_impact_combines_graph_catalog_and_document(client, headers):
    response = client.get("/api/impact/API-002", headers=headers["PER-002"])
    assert response.status_code == 200
    data = response.json()
    assert data["sources"] == ["Neo4j", "PostgreSQL", "MongoDB"]
    assert data["paths"][0]["service"] == "checkout-service"
    assert data["projects"][0]["leader"] == "Ana López"
    assert data["documents"][0]["version_id"] == "VER-001"
    assert data["documents"][0]["content"]["steps"]
    assert data["synchronization_pending"] == 0


def test_unknown_api_returns_404(client, headers):
    assert client.get("/api/impact/API-INEXISTENTE", headers=headers["PER-002"]).status_code == 404


def test_api_without_service_consumers_returns_empty_projects(client, headers):
    response = client.get("/api/impact/API-001", headers=headers["PER-002"])
    assert response.status_code == 200
    assert response.json()["projects"] == []


def test_restricted_document_denies_leader(client, headers):
    assert client.get("/api/documents/DOC-003", headers=headers["PER-001"]).status_code == 403


def test_document_list_filters_restricted_content(client, headers):
    rows = client.get("/api/documents", headers=headers["PER-001"]).json()
    assert "DOC-003" not in {row["document_id"] for row in rows}


def test_technical_reviewer_can_read_restricted_document(client, headers):
    assert client.get("/api/documents/DOC-003", headers=headers["PER-003"]).status_code == 200


def test_postgres_rejects_missing_reference():
    with pytest.raises(psycopg.IntegrityError):
        with connection() as conn:
            conn.execute(
                """INSERT INTO projects(project_id,code,name,department_id,leader_id)
                   VALUES ('TEST-BAD','TEST-BAD','Prueba','DEP-NO-EXISTE','PER-001')"""
            )


def test_postgres_rejects_second_current_version():
    with pytest.raises(psycopg.IntegrityError):
        with connection() as conn:
            conn.execute(
                """INSERT INTO versions(version_id,document_id,number,state,expires_at)
                   VALUES ('TEST-BAD','DOC-001','999.0','VIGENTE',now()+interval '1 day')"""
            )


def test_postgres_rolls_back_partial_transaction():
    with pytest.raises(psycopg.IntegrityError):
        with connection() as conn:
            conn.execute("INSERT INTO departments VALUES ('TEST-ROLLBACK','Temporal de prueba','Temporal')")
            conn.execute("INSERT INTO departments VALUES ('DEP-001','Duplicado','Inválido')")
    with connection() as conn:
        assert conn.execute("SELECT 1 FROM departments WHERE department_id='TEST-ROLLBACK'").fetchone() is None


def test_mongodb_rejects_invalid_document(client):
    with pytest.raises(WriteError):
        client.app.state.service.documents.collection.insert_one({"_id": "TEST-INVALID", "kind": "RUNBOOK"})


def test_mongodb_rejects_wrong_nested_type(client):
    invalid = {
        "_id": "TEST-INVALID", "documentId": "TEST", "kind": "RUNBOOK", "revision": 1,
        "content": {"summary": "Contenido de prueba válido.", "sections": [{"heading": "Alcance", "body": "Prueba"}], "steps": "incorrecto"},
    }
    with pytest.raises(WriteError):
        client.app.state.service.documents.collection.insert_one(invalid)


def test_neo4j_rejects_duplicate_identifier(client):
    with pytest.raises(ConstraintError):
        client.app.state.service.graph.query("CREATE (:Persona {personaId:'PER-001'})")


def test_graph_tests_and_positive_coverage(client):
    graph = client.app.state.service.graph
    for statement in statements(ROOT / "NexusKM/cypher/09_tests.cypher"):
        rows = graph.query(statement)
        if "AS nodos" in statement:
            assert rows[0]["nodos"] >= 63
        elif "AS relaciones" in statement:
            assert rows[0]["relaciones"] >= 87
        else:
            assert rows == [], rows
    assert graph.query("MATCH (n:API {apiId:'API-002'}) RETURN count(n) AS n")[0]["n"] == 1


def test_q2_only_returns_published_current_versions(client):
    query = statements(ROOT / "NexusKM/cypher/08_queries.cypher")[1]
    rows = client.app.state.service.graph.query(query)
    assert len(rows) >= 2
    assert all(row["estado"] == "VIGENTE" for row in rows)


def test_historical_owner_approval_is_corrected(client):
    rows = client.app.state.service.graph.query(
        """MATCH (:Aprobacion {aprobacionId:'APR-004'})-[:EMITIDA_POR]->(p:Persona)
           RETURN p.personaId AS owner"""
    )
    assert rows == [{"owner": "PER-002"}]


def test_idempotent_create_and_conflicting_reuse(client, headers, create_document, write):
    record, payload, key = create_document()
    replay = write("/documents", body=payload, key=key)
    assert replay.status_code == 201
    assert replay.json()["document_id"] == record["document_id"]
    assert replay.json()["replayed"]
    changed = {**payload, "title": "Otra operación"}
    assert write("/documents", body=changed, key=key).status_code == 409
    assert write("/documents", person="PER-004", body=payload, key=key).status_code == 409


def test_create_rename_content_and_soft_delete(client, headers, create_document, write):
    record, payload, _ = create_document()
    document_id, version_id = record["document_id"], record["version_id"]
    renamed = write("/documents/" + document_id, method="PATCH", body={"title": "Runbook actualizado", "expected_revision": 1})
    assert renamed.status_code == 200
    changed_content = copy.deepcopy(payload["content"])
    changed_content["summary"] = "Resumen actualizado de la operación del servicio."
    updated = write("/versions/" + version_id + "/content", method="PUT", body={"content": changed_content, "expected_revision": 1})
    assert updated.status_code == 200
    detail = client.get("/api/documents/" + document_id, headers=headers["PER-005"]).json()
    assert detail["document"]["title"] == "Runbook actualizado"
    assert detail["versions"][0]["content"]["summary"] == changed_content["summary"]
    assert detail["versions"][0]["content_revision"] == 2
    assert write("/documents/" + document_id + "?expected_revision=2", method="DELETE").status_code == 200
    assert client.get("/api/documents/" + document_id, headers=headers["PER-005"]).status_code == 404
    assert client.app.state.service.documents.get(version_id) is not None
    graph_row = client.app.state.service.graph.query(
        "MATCH (d:Documento {documentoId:$id}) RETURN d.activo AS active", id=document_id
    )
    assert graph_row == [{"active": False}]


def test_non_owner_cannot_rename(write):
    response = write("/documents/DOC-001", person="PER-001", method="PATCH", body={"title": "Cambio indebido", "expected_revision": 1})
    assert response.status_code == 403


def test_stale_revision_rejected(create_document, write):
    record, _, _ = create_document()
    url = "/documents/" + record["document_id"]
    assert write(url, method="PATCH", body={"title": "Cambio uno", "expected_revision": 1}).status_code == 200
    assert write(url, method="PATCH", body={"title": "Cambio atrasado", "expected_revision": 1}).status_code == 409


def test_concurrent_updates_have_one_winner(client, headers, create_document):
    record, _, _ = create_document()
    def rename(index):
        return client.patch(
            "/api/documents/" + record["document_id"],
            json={"title": "Edición concurrente " + str(index), "expected_revision": 1},
            headers={**headers["PER-005"], "Idempotency-Key": str(uuid4())},
        ).status_code
    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = list(executor.map(rename, (1, 2)))
    assert sorted(statuses) == [200, 409]


def test_content_validation_before_enqueue(client, headers):
    response = client.post("/api/documents", headers={**headers["PER-005"], "Idempotency-Key": str(uuid4())}, json={
        "title": "Documento inválido", "kind": "RUNBOOK", "classification": "INTERNO",
        "owner_id": "PER-005", "project_id": "PRY-001", "number": "1.0",
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat(),
        "content": {"summary": "Resumen suficientemente largo.", "sections": [{"heading": "Prueba", "body": "Prueba"}]},
    })
    assert response.status_code == 422


@pytest.mark.parametrize("expiration", ["2020-01-01T00:00:00+00:00", "2027-01-01"])
def test_invalid_expiration(client, headers, expiration):
    response = client.post("/api/documents", headers={**headers["PER-005"], "Idempotency-Key": str(uuid4())}, json={
        "title": "Documento inválido", "kind": "RUNBOOK", "classification": "INTERNO",
        "owner_id": "PER-005", "project_id": "PRY-001", "number": "1.0", "expires_at": expiration,
        "content": {"summary": "Resumen suficientemente largo.", "sections": [{"heading": "Prueba", "body": "Prueba"}], "steps": [{"title": "Paso", "instruction": "Verificar"}]},
    })
    assert response.status_code == 422


def test_published_content_is_immutable(write):
    response = write("/versions/VER-001/content", method="PUT", body={
        "expected_revision": 1,
        "content": {"summary": "Resumen suficientemente largo.", "sections": [{"heading": "Prueba", "body": "Prueba"}], "steps": [{"title": "Paso", "instruction": "Verificar"}]},
    })
    assert response.status_code == 409


def test_duplicate_version_number_rejected(create_document, write):
    record, payload, _ = create_document()
    body = {key: payload[key] for key in ("number", "expires_at", "content")}
    assert write("/documents/" + record["document_id"] + "/versions", body=body).status_code == 409


def test_self_technical_approval_rejected(create_document, write):
    record, _, _ = create_document(person="PER-003")
    request = write("/requests", person="PER-003", body={"version_id": record["version_id"]}).json()
    assert write("/requests/" + request["request_id"] + "/approvals", person="PER-003", body={"kind": "TECNICA"}).status_code == 403


def test_wrong_role_and_wrong_owner_approvals_rejected(create_document, write):
    record, _, _ = create_document()
    request_id = write("/requests", body={"version_id": record["version_id"]}).json()["request_id"]
    url = "/requests/" + request_id + "/approvals"
    assert write(url, person="PER-001", body={"kind": "TECNICA"}).status_code == 403
    assert write(url, person="PER-002", body={"kind": "PROPIETARIO"}).status_code == 403


def test_full_approval_and_publication_flow(client, headers, create_document, write):
    record, _, _ = create_document()
    request_id = write("/requests", body={"version_id": record["version_id"]}).json()["request_id"]
    approval_url = "/requests/" + request_id + "/approvals"
    assert write("/requests/" + request_id + "/publish").status_code == 409
    assert write(approval_url, person="PER-003", body={"kind": "TECNICA"}).status_code == 200
    assert write(approval_url, person="PER-003", body={"kind": "TECNICA"}).status_code == 409
    assert write(approval_url, person="PER-006", body={"kind": "TECNICA"}).status_code == 200
    owner_approval = write(approval_url, body={"kind": "PROPIETARIO"})
    assert owner_approval.json()["state"] == "APROBADA"
    published = write("/requests/" + request_id + "/publish")
    assert published.status_code == 200
    assert published.json()["state"] == "PUBLICADA"
    assert write("/requests/" + request_id + "/publish").status_code == 409
    detail = client.get("/api/documents/" + record["document_id"], headers=headers["PER-005"]).json()
    assert detail["versions"][0]["state"] == "VIGENTE"
    assert detail["versions"][0]["content_ready"]
    projected = client.app.state.service.graph.query(
        """MATCH (s:SolicitudCambio {solicitudId:$id})
           MATCH (a:Aprobacion)-[:APRUEBA_SOLICITUD]->(s)
           RETURN s.titulo AS title,s.creadaEn AS created_at,collect(a.fecha) AS dates""",
        id=request_id,
    )[0]
    assert projected["title"] and projected["created_at"]
    assert len(projected["dates"]) == 3


def test_restricted_publication_requires_security(create_document, write):
    record, _, _ = create_document(person="PER-002", classification="RESTRINGIDO")
    request_id = write("/requests", person="PER-002", body={"version_id": record["version_id"]}).json()["request_id"]
    url = "/requests/" + request_id + "/approvals"
    for reviewer in ("PER-003", "PER-006"):
        assert write(url, person=reviewer, body={"kind": "TECNICA"}).status_code == 200
    owner = write(url, person="PER-002", body={"kind": "PROPIETARIO"}).json()
    assert owner["state"] == "PENDIENTE"
    assert write("/requests/" + request_id + "/publish", person="PER-002").status_code == 409
    security = write(url, person="PER-002", body={"kind": "SEGURIDAD"})
    assert security.json()["state"] == "APROBADA"
    assert write("/requests/" + request_id + "/publish", person="PER-002").status_code == 200


def test_partial_write_is_recoverable(client, headers, create_document, write, monkeypatch):
    graph = client.app.state.service.graph
    original = graph.sync_document
    def fail(snapshot):
        raise ServiceUnavailable("Fallo controlado de prueba")
    monkeypatch.setattr(graph, "sync_document", fail)
    record, payload, key = create_document()
    assert record["synchronization"]["pending"] >= 1
    assert graph.query("MATCH (d:Documento {documentoId:$id}) RETURN count(d) AS n", id=record["document_id"]) == [{"n": 0}]
    assert client.app.state.service.documents.get(record["version_id"]) is not None
    monkeypatch.setattr(graph, "sync_document", original)
    retry = client.post("/api/synchronization/retry", headers=headers["PER-004"])
    assert retry.status_code == 200
    assert retry.json()["pending"] == 0
    replay = write("/documents", body=payload, key=key)
    assert replay.json()["replayed"]
    assert graph.query("MATCH (d:Documento {documentoId:$id}) RETURN count(d) AS n", id=record["document_id"]) == [{"n": 1}]


def test_sync_retry_requires_admin(client, headers):
    assert client.post("/api/synchronization/retry", headers=headers["PER-001"]).status_code == 403


def test_audit_is_recorded_and_scoped(client, headers, create_document):
    record, _, _ = create_document()
    own_events = client.get("/api/audit", headers=headers["PER-005"]).json()
    assert any(row["entity_id"] == record["document_id"] for row in own_events)
    assert all(row["actor_id"] == "PER-005" for row in own_events)


def test_sql_input_is_parameterized(client, headers):
    response = client.get("/api/documents/DOC-001%27%20OR%201=1--", headers=headers["PER-002"])
    assert response.status_code == 404
