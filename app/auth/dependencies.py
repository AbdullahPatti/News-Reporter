from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models import User
from app.auth.jwt import verify_token

security = HTTPBearer(auto_error=False)


def _user_from_request(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
    db: Session,
) -> User | None:
    token = None

    if credentials:
        token = credentials.credentials
    elif "access_token" in request.cookies:
        token = request.cookies.get("access_token")

    if not token:
        return None

    payload = verify_token(token)
    if payload is None or payload.get("type"):
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return None

    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None or not user.is_active:
        return None
    return user


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    user = _user_from_request(request, credentials, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_optional_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db)
) -> User | None:
    return _user_from_request(request, credentials, db)