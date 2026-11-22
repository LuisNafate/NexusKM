import base64
import hashlib
import hmac
import json
import secrets
import time

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.errors import DomainError
from backend.repositories.relational import connection
from backend.settings import required

bearer = HTTPBearer(auto_error=False)


def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    value = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 300_000).hex()
    return f"{salt}:{value}"


def check_password(password, saved):
    return hmac.compare_digest(hash_password(password, saved.split(":")[0]), saved)


def issue_token(person_id):
    payload = json.dumps({"sub": person_id, "exp": int(time.time()) + 3600}, separators=(",", ":"))
    encoded = base64.urlsafe_b64encode(payload.encode()).rstrip(b"=")
    signature = hmac.new(required("TOKEN_SECRET").encode(), encoded, hashlib.sha256).hexdigest()
    return encoded.decode() + "." + signature


def decode_token(token):
    try:
        encoded, signature = token.split(".")
        expected = hmac.new(required("TOKEN_SECRET").encode(), encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("signature")
        payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
        if payload["exp"] <= time.time() or not isinstance(payload["sub"], str):
            raise ValueError("expired")
        return payload["sub"]
    except (ValueError, KeyError, TypeError):
        raise DomainError(401, "Sesión inválida o vencida.") from None


def current_person(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    if not credentials:
        raise DomainError(401, "Inicia sesión para continuar.")
    person_id = decode_token(credentials.credentials)
    with connection() as conn:
        person = conn.execute(
            "SELECT person_id, name, role, department_id FROM people WHERE person_id=%s AND active",
            (person_id,),
        ).fetchone()
    if not person:
        raise DomainError(401, "La cuenta está inactiva.")
    return person
