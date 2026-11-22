import json
import os

from pymongo import MongoClient

from backend.errors import DomainError
from backend.settings import ROOT, required


class DocumentRepository:
    def __init__(self):
        self.client = MongoClient(
            host=os.getenv("MONGO_HOST", "127.0.0.1"),
            port=int(os.getenv("MONGO_PORT", "57017")),
            username=os.getenv("MONGO_USER", "nexuskm"),
            password=required("MONGO_PASSWORD"),
            serverSelectionTimeoutMS=2000,
            connectTimeoutMS=2000,
            socketTimeoutMS=3000,
        )
        self.db = self.client["nexuskm"]
        self.collection = self.db["versions"]

    def setup(self):
        validator = json.loads((ROOT / "database/document/validator.json").read_text(encoding="utf-8"))
        if "versions" in self.db.list_collection_names():
            self.db.command("collMod", "versions", validator=validator, validationLevel="strict")
        else:
            self.db.create_collection("versions", validator=validator, validationLevel="strict")
        self.collection.create_index([("documentId", 1), ("revision", 1)], name="document_versions")

    def ping(self):
        return self.client.admin.command("ping")["ok"] == 1

    def get(self, version_id):
        return self.collection.find_one({"_id": version_id})

    def upsert(self, payload):
        self.collection.replace_one({"_id": payload["_id"]}, payload, upsert=True)

    def close(self):
        self.client.close()


def validate_content(kind, content):
    required_array = {"RUNBOOK": "steps", "API": "endpoints", "SEGURIDAD": "threats"}[kind]
    fields = {
        "steps": ("title", "instruction"),
        "endpoints": ("path", "method"),
        "threats": ("title", "mitigation"),
    }[required_array]
    rows = content.get(required_array)
    if not rows or any(any(not row.get(field, "").strip() for field in fields) for row in rows):
        raise DomainError(422, f"El contenido {kind} requiere {required_array} con {', '.join(fields)}.")
