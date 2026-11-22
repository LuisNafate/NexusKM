from psycopg.types.json import Jsonb

from backend.repositories.relational import connection


def enqueue(conn, document_id, payload=None, action="SYNC"):
    conn.execute(
        "INSERT INTO outbox(document_id, action, payload) VALUES (%s,%s,%s)",
        (document_id, action, Jsonb(payload) if payload else None),
    )


def snapshot(conn, document_id):
    document = conn.execute(
        "SELECT * FROM documents WHERE document_id=%s FOR UPDATE", (document_id,)
    ).fetchone()
    versions = conn.execute(
        "SELECT * FROM versions WHERE document_id=%s ORDER BY version_id", (document_id,)
    ).fetchall()
    requests = conn.execute(
        """SELECT r.* FROM change_requests r JOIN versions v USING(version_id)
           WHERE v.document_id=%s""",
        (document_id,),
    ).fetchall()
    approvals = conn.execute(
        """SELECT a.* FROM approvals a JOIN change_requests r USING(request_id)
           JOIN versions v USING(version_id) WHERE v.document_id=%s""",
        (document_id,),
    ).fetchall()
    current = any(v["state"] == "VIGENTE" for v in versions)
    return {
        "document": {
            **document,
            "state": "RETIRADO" if not document["active"] else ("PUBLICADO" if current else "EN_REVISION"),
        },
        "versions": [
            {
                "document_id": document_id,
                "version_id": v["version_id"],
                "number": v["number"],
                "state": v["state"],
                "expires_at": v["expires_at"].isoformat(),
                "published_at": v["published_at"].isoformat() if v["published_at"] else None,
            }
            for v in versions
        ],
        "requests": requests,
        "approvals": approvals,
    }


def pending_count(document_id=None):
    with connection() as conn:
        return conn.execute(
            """SELECT count(*) AS count FROM outbox WHERE state='PENDIENTE'
               AND (%s::text IS NULL OR document_id=%s)""",
            (document_id, document_id),
        ).fetchone()["count"]


def process_pending(documents, graph, limit=30):
    processed = 0
    failed = 0
    for _ in range(limit):
        with connection() as conn:
            event = conn.execute(
                """
                SELECT o.* FROM outbox o
                WHERE o.state='PENDIENTE' AND NOT EXISTS (
                    SELECT 1 FROM outbox earlier
                    WHERE earlier.document_id=o.document_id AND earlier.state='PENDIENTE'
                      AND earlier.event_id<o.event_id
                )
                ORDER BY o.event_id FOR UPDATE SKIP LOCKED LIMIT 1
                """
            ).fetchone()
            if not event:
                break
            try:
                state = snapshot(conn, event["document_id"])
                if event["payload"]:
                    documents.upsert(event["payload"])
                graph.sync_document(state)
            except Exception as error:
                conn.execute(
                    "UPDATE outbox SET attempts=attempts+1,last_error=%s WHERE event_id=%s",
                    (type(error).__name__, event["event_id"]),
                )
                failed += 1
            else:
                conn.execute(
                    """UPDATE outbox SET state='COMPLETA',attempts=attempts+1,last_error=NULL,
                       payload=NULL,completed_at=now() WHERE event_id=%s""",
                    (event["event_id"],),
                )
                processed += 1
        if failed:
            break
    return {"processed": processed, "failed": failed, "pending": pending_count()}
