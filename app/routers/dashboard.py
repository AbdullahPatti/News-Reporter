from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi import Header, HTTPException
from app.services.scheduler import pre_fetch_and_summarize, run_morning_digest, force_send_digest
from app.services.email_builder import get_landing_preview
from app.config import settings

from app.auth.dependencies import get_optional_user
from app.auth.jwt import verify_token
from app.database import get_db
from app.models import User
import uuid

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")
PKT = ZoneInfo("Asia/Karachi")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user: User | None = Depends(get_optional_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user": user}
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"user": None}
    )


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"user": None}
    )


@router.get("/verify", response_class=HTMLResponse)
def verify_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="verify.html",
        context={"user": None}
    )


@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html",
        context={"user": None}
    )


@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(request: Request, token: str = "", user: User | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    payload = verify_token(token) if token else None
    valid = bool(payload and payload.get("type") == "password_reset")
    return templates.TemplateResponse(
        request=request,
        name="reset_password.html",
        context={"user": None, "token": token, "valid": valid}
    )


@router.get("/dashboard/preferences", response_class=HTMLResponse)
def preferences_page(request: Request, user: User | None = Depends(get_optional_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="preferences.html",
        context={"user": user}
    )


@router.post("/dashboard/preferences")
def update_preferences(
    preferred_hour: int = Form(...),
    full_name: str = Form(None),
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    if preferred_hour < 6 or preferred_hour > 10:
        return RedirectResponse(url="/dashboard/preferences", status_code=303)

    user.preferred_hour = preferred_hour
    if full_name is not None:
        user.full_name = full_name.strip() or None

    db.commit()
    return RedirectResponse(url="/dashboard", status_code=303)


@router.get("/", response_class=HTMLResponse)
def landing_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    stories = get_landing_preview(db, limit=2)
    today_str = datetime.now(PKT).strftime("%A, %d %B %Y")
    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context={"user": user, "stories": stories, "today_str": today_str}
    )


@router.get("/unsubscribe", response_class=HTMLResponse)
def unsubscribe(
    request: Request,
    token: str = "",
    db: Session = Depends(get_db),
):
    payload = verify_token(token) if token else None
    unsubscribed = False
    if payload and payload.get("type") == "unsubscribe":
        try:
            user_uuid = uuid.UUID(payload.get("sub", ""))
        except ValueError:
            user_uuid = None
        if user_uuid:
            user = db.query(User).filter(User.id == user_uuid).first()
            if user:
                user.is_active = False
                db.commit()
                unsubscribed = True
    return templates.TemplateResponse(
        request=request,
        name="unsubscribe.html",
        context={"user": None, "unsubscribed": unsubscribed}
    )


@router.post("/internal/run-prefetch")
def trigger_prefetch(x_internal_key: str = Header(None)):
    """Manually trigger news fetch + summarization"""
    if settings.INTERNAL_API_KEY and x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid internal key")

    pre_fetch_and_summarize()
    return {"status": "prefetch completed"}


@router.post("/internal/run-digest")
def trigger_digest(x_internal_key: str = Header(None)):
    """Manually trigger digest sending — works at any time of day"""
    if settings.INTERNAL_API_KEY and x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid internal key")

    result = force_send_digest()
    return {"status": "digest job completed", **result}

