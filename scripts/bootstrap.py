import json
from datetime import datetime, timedelta, timezone

from backend.auth import hash_password
from backend.repositories.document import DocumentRepository
from backend.repositories.graph import GraphRepository
from backend.repositories.relational import connection
from backend.settings import ROOT, required
from backend.synchronization import enqueue, process_pending

DEPARTMENTS = [
    ("DEP-001", "Desarrollo", "Construcción y mantenimiento de software"),
    ("DEP-002", "Seguridad", "Seguridad de aplicaciones y cumplimiento"),
    ("DEP-003", "Arquitectura", "Arquitectura empresarial y estándares"),
    ("DEP-004", "Operaciones", "Disponibilidad y operación de plataformas"),
]
PEOPLE = [
    ("PER-001", "Ana López", "ana.lopez@nexuskm.test", "DEP-001", "LIDER"),
    ("PER-002", "Carlos Ruiz", "carlos.ruiz@nexuskm.test", "DEP-002", "SEGURIDAD"),
    ("PER-003", "Laura García", "laura.garcia@nexuskm.test", "DEP-003", "TECNICO"),
    ("PER-004", "Miguel Torres", "miguel.torres@nexuskm.test", "DEP-004", "ADMIN"),
    ("PER-005", "Sofía Herrera", "sofia.herrera@nexuskm.test", "DEP-001", "PROPIETARIO"),
    ("PER-006", "Diego Pérez", "diego.perez@nexuskm.test", "DEP-003", "TECNICO"),
]
PROJECTS = [
    ("PRY-001", "CHECKOUT", "Sistema Checkout", "DEP-001", "PER-001"),
    ("PRY-002", "INVENTARIO", "Sistema Inventario", "DEP-003", "PER-003"),
]
DOCUMENTS = [
    ("DOC-001", "Runbook de pagos", "RUNBOOK", "INTERNO", "PER-005", "PRY-001"),
    ("DOC-002", "Contrato API de inventario", "API", "INTERNO", "PER-006", "PRY-002"),
    ("DOC-003", "Modelo de amenazas checkout", "SEGURIDAD", "RESTRINGIDO", "PER-002", "PRY-001"),
]


def statements(path):
    return [statement.strip() for statement in path.read_text(encoding="utf-8").split(";") if statement.strip()]


def bootstrap():
    documents = DocumentRepository()
    graph = GraphRepository()
    try:
        documents.setup()
        graph.ping()
        with connection() as conn:
            conn.execute("SELECT pg_advisory_xact_lock(hashtext('NEXUSKM_BOOTSTRAP'))")
            conn.execute((ROOT / "database/relational/schema.sql").read_text(encoding="utf-8"))
            conn.execute("CREATE TABLE IF NOT EXISTS bootstrap_state (key text PRIMARY KEY, initialized_at timestamptz NOT NULL DEFAULT now())")
            initialized = conn.execute("SELECT 1 FROM bootstrap_state WHERE key='v1'").fetchone()
            if not initialized:
                for department in DEPARTMENTS:
                    conn.execute("INSERT INTO departments VALUES (%s,%s,%s)", department)
                for person in PEOPLE:
                    conn.execute(
                        """INSERT INTO people(person_id,name,email,department_id,role,password_hash)
                           VALUES (%s,%s,%s,%s,%s,%s)""",
                        (*person, hash_password(required("DEMO_PASSWORD"))),
                    )
                for project in PROJECTS:
                    conn.execute(
                        "INSERT INTO projects(project_id,code,name,department_id,leader_id) VALUES (%s,%s,%s,%s,%s)",
                        project,
                    )
                for document in DOCUMENTS:
                    conn.execute(
                        """INSERT INTO documents(document_id,title,kind,classification,owner_id,project_id)
                           VALUES (%s,%s,%s,%s,%s,%s)""",
                        document,
                    )
                expires = datetime.now(timezone.utc) + timedelta(days=180)
                for row in [
                    ("VER-001", "DOC-001", "1.0", "VIGENTE"),
                    ("VER-002", "DOC-002", "2.1", "VIGENTE"),
                    ("VER-003", "DOC-003", "0.9", "EN_REVISION"),
                ]:
                    conn.execute(
                        """INSERT INTO versions(version_id,document_id,number,state,expires_at,published_at)
                           VALUES (%s,%s,%s,%s,%s,%s)""",
                        (*row, expires, datetime.now(timezone.utc) if row[3] == "VIGENTE" else None),
                    )
                conn.execute(
                    """INSERT INTO change_requests(request_id,version_id,requester_id,state)
                       VALUES ('SOL-001','VER-003','PER-005','APROBADA')"""
                )
                for approval in [
                    ("APR-001", "SOL-001", "PER-003", "TECNICA"),
                    ("APR-002", "SOL-001", "PER-006", "TECNICA"),
                    ("APR-003", "SOL-001", "PER-002", "SEGURIDAD"),
                    ("APR-004", "SOL-001", "PER-002", "PROPIETARIO"),
                ]:
                    conn.execute(
                        "INSERT INTO approvals(approval_id,request_id,reviewer_id,kind) VALUES (%s,%s,%s,%s)",
                        approval,
                    )
                for path in sorted((ROOT / "NexusKM/cypher").glob("*.cypher")):
                    if path.name[:2] in ("00", "08", "09"):
                        continue
                    for statement in statements(path):
                        graph.query(statement)
                content = json.loads((ROOT / "database/document/seed.json").read_text(encoding="utf-8"))
                for payload in content:
                    enqueue(conn, payload["documentId"], payload)
                conn.execute("INSERT INTO audit_events(actor_id,action,entity_id) VALUES (NULL,'CARGA_INICIAL','NEXUSKM')")
                conn.execute("INSERT INTO bootstrap_state(key) VALUES ('v1')")
        result = process_pending(documents, graph, limit=100)
        print(json.dumps({"bootstrap": "ready", "synchronization": result}))
        if result["pending"]:
            raise RuntimeError("La carga conserva sincronizaciones pendientes. Revisa los servicios y reintenta.")
    finally:
        documents.close()
        graph.close()


if __name__ == "__main__":
    bootstrap()
