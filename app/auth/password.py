import bcrypt
import hashlib
import base64


def _prepare_password(password: str) -> bytes:
    """
    Pre-hash the password with SHA-256 to safely handle passwords longer
    than bcrypt's 72-byte limit, then base64-encode for bcrypt compatibility.
    """
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest)


def hash_password(password: str) -> str:
    prepared = _prepare_password(password)
    hashed = bcrypt.hashpw(prepared, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    prepared = _prepare_password(plain_password)
    return bcrypt.checkpw(prepared, hashed_password.encode("utf-8"))