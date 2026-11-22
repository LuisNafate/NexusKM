import secrets
from pathlib import Path


def setup():
    root = Path(__file__).resolve().parent.parent
    target = root / ".env"
    if target.exists():
        print("El archivo .env ya existe.")
        return
    values = {
        "POSTGRES_DB": "nexuskm",
        "POSTGRES_USER": "nexuskm",
        "POSTGRES_PASSWORD": secrets.token_urlsafe(24),
        "POSTGRES_PORT": "55432",
        "MONGO_USER": "nexuskm",
        "MONGO_PASSWORD": secrets.token_urlsafe(24),
        "MONGO_PORT": "57017",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": secrets.token_urlsafe(24),
        "NEO4J_BOLT_PORT": "57687",
        "NEO4J_HTTP_PORT": "57474",
        "APP_PORT": "58000",
        "TOKEN_SECRET": secrets.token_urlsafe(48),
        "DEMO_PASSWORD": secrets.token_urlsafe(18),
    }
    target.write_text("\n".join(f"{key}={value}" for key, value in values.items()) + "\n", encoding="utf-8")
    print("Configuración local creada en .env. La contraseña de acceso es DEMO_PASSWORD.")


if __name__ == "__main__":
    setup()
