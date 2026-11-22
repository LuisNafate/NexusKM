CREATE TABLE IF NOT EXISTS departments (
    department_id text PRIMARY KEY,
    name text NOT NULL UNIQUE,
    description text NOT NULL
);
CREATE TABLE IF NOT EXISTS people (
    person_id text PRIMARY KEY,
    name text NOT NULL,
    email text NOT NULL UNIQUE,
    department_id text NOT NULL REFERENCES departments,
    role text NOT NULL CHECK (role IN ('LIDER','TECNICO','SEGURIDAD','PROPIETARIO','ADMIN')),
    password_hash text NOT NULL,
    active boolean NOT NULL DEFAULT true
);
CREATE TABLE IF NOT EXISTS projects (
    project_id text PRIMARY KEY,
    code text NOT NULL UNIQUE,
    name text NOT NULL,
    department_id text NOT NULL REFERENCES departments,
    leader_id text NOT NULL REFERENCES people,
    active boolean NOT NULL DEFAULT true
);
CREATE TABLE IF NOT EXISTS documents (
    document_id text PRIMARY KEY,
    title text NOT NULL CHECK (length(trim(title)) BETWEEN 3 AND 160),
    kind text NOT NULL CHECK (kind IN ('RUNBOOK','API','SEGURIDAD')),
    classification text NOT NULL CHECK (classification IN ('INTERNO','RESTRINGIDO')),
    owner_id text NOT NULL REFERENCES people,
    project_id text NOT NULL REFERENCES projects,
    active boolean NOT NULL DEFAULT true,
    revision integer NOT NULL DEFAULT 1 CHECK (revision > 0)
);
CREATE TABLE IF NOT EXISTS versions (
    version_id text PRIMARY KEY,
    document_id text NOT NULL REFERENCES documents,
    number text NOT NULL,
    state text NOT NULL CHECK (state IN ('BORRADOR','EN_REVISION','VIGENTE','RETIRADA')),
    expires_at timestamptz NOT NULL,
    published_at timestamptz,
    content_revision integer NOT NULL DEFAULT 1 CHECK (content_revision>0),
    UNIQUE (document_id, number)
);
CREATE UNIQUE INDEX IF NOT EXISTS one_current_version
    ON versions(document_id) WHERE state='VIGENTE';
CREATE INDEX IF NOT EXISTS document_project ON documents(project_id) WHERE active;
CREATE INDEX IF NOT EXISTS version_expiration ON versions(expires_at);
CREATE TABLE IF NOT EXISTS change_requests (
    request_id text PRIMARY KEY,
    version_id text NOT NULL REFERENCES versions,
    requester_id text NOT NULL REFERENCES people,
    state text NOT NULL DEFAULT 'PENDIENTE'
        CHECK (state IN ('PENDIENTE','APROBADA','PUBLICADA','CANCELADA')),
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS one_open_request ON change_requests(version_id)
    WHERE state IN ('PENDIENTE','APROBADA');
CREATE TABLE IF NOT EXISTS approvals (
    approval_id text PRIMARY KEY,
    request_id text NOT NULL REFERENCES change_requests,
    reviewer_id text NOT NULL REFERENCES people,
    kind text NOT NULL CHECK (kind IN ('TECNICA','SEGURIDAD','PROPIETARIO')),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (request_id, reviewer_id, kind)
);
CREATE TABLE IF NOT EXISTS audit_events (
    event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    actor_id text REFERENCES people,
    action text NOT NULL,
    entity_id text NOT NULL,
    details jsonb NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS audit_entity_date ON audit_events(entity_id, created_at);
CREATE TABLE IF NOT EXISTS operations (
    operation_id uuid PRIMARY KEY,
    actor_id text NOT NULL REFERENCES people,
    action text NOT NULL,
    request_hash text NOT NULL,
    response jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS outbox (
    event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id text NOT NULL REFERENCES documents,
    action text NOT NULL CHECK (action IN ('SYNC','DELETE')),
    payload jsonb,
    state text NOT NULL DEFAULT 'PENDIENTE' CHECK (state IN ('PENDIENTE','COMPLETA')),
    attempts integer NOT NULL DEFAULT 0,
    last_error text,
    created_at timestamptz NOT NULL DEFAULT now(),
    completed_at timestamptz
);
CREATE INDEX IF NOT EXISTS pending_events ON outbox(event_id) WHERE state='PENDIENTE';
