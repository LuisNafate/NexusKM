"""Verify a separately launched, empty Compose installation without exposing secrets."""
import json
import subprocess
import time
from datetime import datetime, timezone

import httpx

from backend.repositories.document import DocumentRepository
from backend.repositories.graph import GraphRepository
from backend.repositories.relational import connection
from backend.settings import ROOT, required


def counts():
    documents = DocumentRepository()
    graph = GraphRepository()
    try:
        with connection() as conn:
            sql_counts = conn.execute(
                """SELECT (SELECT count(*) FROM documents) AS documents,
                   (SELECT count(*) FROM versions) AS versions,
                   (SELECT count(*) FROM people) AS people,
                   (SELECT count(*) FROM outbox WHERE state='PENDIENTE') AS pending,
                   (SELECT min(expires_at)::text FROM versions) AS expires_at"""
            ).fetchone()
        return {
            "postgresql": sql_counts,
            "mongodb": documents.collection.count_documents({}),
            "neo4j": graph.query("MATCH (n) RETURN count(n) AS nodes")[0]["nodes"],
            "relationships": graph.query("MATCH ()-[r]->() RETURN count(r) AS n")[0]["n"],
        }
    finally:
        documents.close()
        graph.close()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    if not args.project.startswith("nexuskm-repro-"):
        raise ValueError("Use an isolated nexuskm-repro- project.")
    with httpx.Client(base_url=f"http://127.0.0.1:{args.port}", timeout=10) as client:
        health = client.get("/api/health")
        health.raise_for_status()
        login = client.post("/api/auth/login", json={"person_id": "PER-002", "password": required("DEMO_PASSWORD")})
        login.raise_for_status()
        client.headers["Authorization"] = "Bearer " + login.json()["access_token"]
        impact = client.get("/api/impact/API-002")
        impact.raise_for_status()
        assert set(impact.json()["sources"]) == {"Neo4j", "PostgreSQL", "MongoDB"}
        before = counts()
        assert before["postgresql"]["documents"] == before["postgresql"]["versions"] == before["mongodb"] == 3
        assert before["postgresql"]["people"] == 6
        assert before["postgresql"]["pending"] == 0
        assert before["neo4j"] == 63 and before["relationships"] == 87
        subprocess.run(["docker", "compose", "-p", args.project, "restart", "app"], cwd=ROOT, check=True, capture_output=True)
        for _ in range(60):
            try:
                response = client.get("/api/health")
                if response.status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(1)
        else:
            raise RuntimeError("App did not recover after restart.")
        after = counts()
        assert after == before, "Restart changed the seed or its dates."
        report = {
            "executed_at_utc": datetime.now(timezone.utc).isoformat(),
            "project": args.project,
            "commands": [f"docker compose -p {args.project} up -d --build --wait --wait-timeout 240", f"docker compose -p {args.project} restart app"],
            "environment": "Isolated Docker Compose project, fresh volumes, alternate localhost ports",
            "health": health.json(),
            "before_restart": before,
            "after_restart": after,
            "impact_sources": impact.json()["sources"],
            "passed": True,
        }
        path = ROOT / "docs/pruebas/evidencias/reconstruccion.json"
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"passed": True, "counts": after}))


if __name__ == "__main__":
    main()
