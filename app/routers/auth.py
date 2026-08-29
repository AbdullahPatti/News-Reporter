from datetime import timedelta, datetime, timezone
import random
import string
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    UserVerify,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token, verify_token
from app.auth.dependencies import get_current_user
from app.config import settings
from app.services.email_sender import send_otp_email, send_password_reset_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _issue_session(user: User) -> JSONResponse:
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"}
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production",
    )
    return response


def _new_otp() -> tuple[str, datetime]:
    code = "".join(random.choices(string.digits, k=6))
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    return code, expires


def _is_expired(when: datetime | None) -> bool:
    if when is None:
        return True
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when < datetime.now(timezone.utc)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        preferred_hour=user_data.preferred_hour,
        is_verified=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return _issue_session(new_user)


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    return _issue_session(user)


@router.post("/verify", response_model=Token)
def verify_email(data: UserVerify, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Already verified")

    if not user.verification_code or user.verification_code != data.code:
        raise HTTPException(status_code=400, detail="Invalid code")

    if _is_expired(user.verification_code_expires_at):
        raise HTTPException(status_code=400, detail="Code expired")

    user.is_verified = True
    user.verification_code = None
    user.verification_code_expires_at = None
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    return _issue_session(user)


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email, User.is_active == True).first()
    if user and user.is_verified:
        token = create_access_token(
            data={"sub": str(user.id), "type": "password_reset"},
            expires_delta=timedelta(hours=1),
        )
        reset_url = f"{settings.APP_BASE_URL.rstrip('/')}/reset-password?token={token}"
        msg_id = send_password_reset_email(user.email, reset_url)
        if not msg_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password reset email. If you are the admin, please verify your domain in Resend."
            )

    return {"detail": "If that email is registered, we sent a reset link."}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    payload = verify_token(data.token)
    if not payload or payload.get("type") != "password_reset":
        raise HTTPException(status_code=400, detail="This reset link is invalid or has expired")

    try:
        user_uuid = uuid.UUID(payload.get("sub", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="This reset link is invalid or has expired")

    user = db.query(User).filter(User.id == user_uuid, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=400, detail="This reset link is invalid or has expired")

    user.hashed_password = hash_password(data.password)
    db.commit()
    return {"detail": "Password updated. You can sign in now."}


@router.post("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
