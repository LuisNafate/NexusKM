from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from backend.settings import postgres_parameters


@contextmanager
def connection():
    with psycopg.connect(**postgres_parameters(), row_factory=dict_row) as conn:
        yield conn


def audit(conn, actor, action, entity_id, details=None):
    conn.execute(
        "INSERT INTO audit_events(actor_id, action, entity_id, details) VALUES (%s,%s,%s,%s)",
        (actor, action, entity_id, Jsonb(details or {})),
    )
