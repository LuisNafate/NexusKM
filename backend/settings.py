import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def required(name):
    value = os.getenv(name)
    if not value or value.startswith("replace-"):
        raise RuntimeError(f"Configura {name} en el entorno local.")
    return value


def postgres_parameters():
    return {
        "host": os.getenv("POSTGRES_HOST", "127.0.0.1"),
        "port": int(os.getenv("POSTGRES_PORT", "55432")),
        "dbname": os.getenv("POSTGRES_DB", "nexuskm"),
        "user": os.getenv("POSTGRES_USER", "nexuskm"),
        "password": required("POSTGRES_PASSWORD"),
        "connect_timeout": 3,
    }
