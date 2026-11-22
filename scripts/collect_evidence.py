import json
import math
import platform
import re
import statistics
import subprocess
import time
from datetime import datetime, timezone
from xml.etree import ElementTree

import httpx
from psycopg import sql

from backend.repositories.document import DocumentRepository
from backend.repositories.graph import GraphRepository
from backend.repositories.relational import connection
from backend.settings import ROOT, required
from scripts.bootstrap import statements


def labeled_queries(path):
    label = None
    for statement in statements(path):
        match = re.search(r"//\s*([QT][0-9]+)\.", statement)
        if match:
            label = match.group(1)
        yield label, statement


def collect():
    destination = ROOT / "docs/pruebas/evidencias"
    destination.mkdir(parents=True, exist_ok=True)
    documents = DocumentRepository()
    graph = GraphRepository()
    try:
        with connection() as conn:
            tables = {}
            for name in ("departments", "people", "projects", "documents", "versions", "change_requests", "approvals", "audit_events", "operations", "outbox"):
                row = conn.execute(sql.SQL("SELECT count(*) AS n FROM {}").format(sql.Identifier(name))).fetchone()
                tables[name] = row["n"]
            postgres_version = conn.execute("SHOW server_version").fetchone()["server_version"]
            schema = conn.execute(
                """SELECT table_name,column_name,data_type,is_nullable,column_default
                   FROM information_schema.columns WHERE table_schema='public'
                   ORDER BY table_name,ordinal_position"""
            ).fetchall()
            sql_queries = []
            for index, statement in enumerate((ROOT / 'database/relational/queries.sql').read_text(encoding='utf-8').split(';'), 1):
                if statement.strip():
                    sql_queries.append({'id': f'S{index}', 'query': statement.strip(), 'result': conn.execute(statement).fetchall()})
        (destination / "esquema-relacional.json").write_text(
            json.dumps(schema, ensure_ascii=False, indent=2, default=str), encoding="utf-8",
        )
        queries = [
            {"id": label, "query": statement, "result": graph.query(statement)}
            for label, statement in labeled_queries(ROOT / "NexusKM/cypher/08_queries.cypher")
        ]
        tests = []
        for label, statement in labeled_queries(ROOT / "NexusKM/cypher/09_tests.cypher"):
            result = graph.query(statement)
            passed = len(result) == 0
            if label == "T10":
                passed = all(value >= minimum for row in result for key, value in row.items()
                             for minimum in [63 if key == "nodos" else 87])
            tests.append({"id": label, "query": statement, "passed": passed, "result": result})
        assert all(test["passed"] for test in tests)
        counts = {
            "nodes": graph.query("MATCH (n) RETURN count(n) AS n")[0]["n"],
            "relationships": graph.query("MATCH ()-[r]->() RETURN count(r) AS n")[0]["n"],
            "labels": graph.query("CALL db.labels() YIELD label RETURN count(label) AS n")[0]["n"],
            "constraints": len(graph.query("SHOW CONSTRAINTS")),
            "indexes": len(graph.query("SHOW INDEXES")),
        }
        with httpx.Client(base_url="http://127.0.0.1:58000", timeout=15) as client:
            health = client.get("/api/health")
            health.raise_for_status()
            login = client.post("/api/auth/login", json={"person_id": "PER-002", "password": required("DEMO_PASSWORD")})
            login.raise_for_status()
            client.headers["Authorization"] = "Bearer " + login.json()["access_token"]
            impact = client.get("/api/impact/API-002")
            impact.raise_for_status()
            performance = {}
            for path in ("/api/impact/API-002", "/api/documents/DOC-001", "/api/requests"):
                durations = []
                for _ in range(30):
                    started = time.perf_counter()
                    response = client.get(path)
                    durations.append((time.perf_counter() - started) * 1000)
                    response.raise_for_status()
                ordered = sorted(durations)
                performance[path] = {
                    "samples": len(durations),
                    "median_ms": round(statistics.median(durations), 2),
                    "p95_ms": round(ordered[math.ceil(len(ordered) * .95) - 1], 2),
                    "max_ms": round(max(durations), 2),
                }
        junit = ElementTree.parse(destination / "pytest.xml").getroot()
        suites = list(junit.iter("testsuite"))
        pytest_result = {
            name: sum(int(suite.get(name, 0)) for suite in suites)
            for name in ("tests", "failures", "errors", "skipped")
        }
        pytest_result["seconds"] = round(sum(float(suite.get("time", 0)) for suite in suites), 3)
        report = {
            "executed_at_utc": datetime.now(timezone.utc).isoformat(),
            "environment": {
                "host": platform.platform(), "python": platform.python_version(),
                "postgresql": postgres_version, "mongodb": documents.client.server_info()["version"],
                "neo4j": graph.query("CALL dbms.components() YIELD versions,edition RETURN versions,edition"),
                "scope": "Docker Compose local, datos ficticios, un cliente secuencial, 30 muestras por operación",
            },
            "health": health.json(), "relational_counts": tables,
            "document_count": documents.collection.count_documents({}),
            "graph_counts": counts,
            "graph_tests": tests, "graph_queries": queries,
            "sql_queries": sql_queries,
            "document_queries": [
                {"id": "D1", "filter": {"_id": "VER-001"}, "result": documents.get("VER-001")},
                {"id": "D2", "filter": {"documentId": "DOC-001"}, "result": list(documents.collection.find({"documentId": "DOC-001"}, {"_id": 1, "kind": 1, "revision": 1, "content.summary": 1}))},
                {"id": "D3", "filter": {"kind": "RUNBOOK", "content.steps.0": {"$exists": True}}, "result": list(documents.collection.find({"kind": "RUNBOOK", "content.steps.0": {"$exists": True}}))},
                {"id": "D4", "filter": {"kind": "API", "content.endpoints.method": "GET"}, "result": list(documents.collection.find({"kind": "API", "content.endpoints.method": "GET"}))},
            ],
            "pytest": pytest_result, "impact": impact.json(), "performance": performance,
        }
        (destination / "verificacion-integrada.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8",
        )
        (ROOT / "docs/api").mkdir(exist_ok=True)
        from backend.main import app
        (ROOT / "docs/api/openapi.json").write_text(
            json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
        )
        print(json.dumps({
            "pytest": pytest_result, "graph": counts, "mongodb_documents": report["document_count"],
            "performance": performance,
        }, ensure_ascii=False))
    finally:
        documents.close()
        graph.close()


if __name__ == "__main__":
    collect()
