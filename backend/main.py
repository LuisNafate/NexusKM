import asyncio
from contextlib import asynccontextmanager, suppress

import psycopg
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from neo4j.exceptions import Neo4jError, ServiceUnavailable, SessionExpired
from pymongo.errors import PyMongoError

from backend.api import router
from backend.errors import DomainError
from backend.repositories.document import DocumentRepository
from backend.repositories.graph import GraphRepository
from backend.service import NexusService
from backend.settings import ROOT
from backend.synchronization import process_pending


@asynccontextmanager
async def lifespan(app):
    app.state.service = NexusService(DocumentRepository(), GraphRepository())

    async def synchronize():
        while True:
            try:
                await asyncio.to_thread(
                    process_pending, app.state.service.documents, app.state.service.graph,
                )
            except (psycopg.Error, PyMongoError, Neo4jError, ServiceUnavailable):
                pass
            await asyncio.sleep(10)

    worker = asyncio.create_task(synchronize())
    yield
    worker.cancel()
    with suppress(asyncio.CancelledError):
        await worker
    app.state.service.documents.close()
    app.state.service.graph.close()


app = FastAPI(
    title="NexusKM API",
    version="1.0.0",
    description="Gestión de conocimiento técnico integrada con PostgreSQL, MongoDB y Neo4j.",
    lifespan=lifespan,
)
app.include_router(router)
app.mount("/static", StaticFiles(directory=ROOT / "frontend"), name="static")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(ROOT / "frontend/index.html")


@app.exception_handler(DomainError)
def domain_error(request: Request, error: DomainError):
    return JSONResponse({"detail": error.message}, status_code=error.status)


@app.exception_handler(psycopg.IntegrityError)
def integrity_error(request: Request, error):
    return JSONResponse({"detail": "La operación viola una regla de unicidad o referencia."}, status_code=409)


async def unavailable(request: Request, error):
    return JSONResponse(
        {"detail": "Una base requerida está temporalmente indisponible. Reintenta con la misma clave de operación."},
        status_code=503,
    )


for error_type in (psycopg.OperationalError, PyMongoError, Neo4jError, ServiceUnavailable, SessionExpired):
    app.add_exception_handler(error_type, unavailable)
