from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi import Header, HTTPException
from app.services.scheduler import pre_fetch_and_summarize, run_morning_digest
from app.config import settings

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import User

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user": current_user}
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"user": None}
    )


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"user": None}
    )


@router.get("/verify", response_class=HTMLResponse)
def verify_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="verify.html",
        context={"user": None}
    )


@router.get("/dashboard/preferences", response_class=HTMLResponse)
def preferences_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        request=request,
        name="preferences.html",
        context={"user": current_user}
    )


@router.post("/dashboard/preferences")
def update_preferences(
    preferred_hour: int = Form(...),
    full_name: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if preferred_hour < 6 or preferred_hour > 10:
        return RedirectResponse(url="/dashboard/preferences", status_code=303)

    current_user.preferred_hour = preferred_hour
    if full_name is not None:
        current_user.full_name = full_name.strip() or None

    db.commit()
    return RedirectResponse(url="/dashboard", status_code=303)

@router.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context={"user": None}
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
    """Manually trigger the morning digest sending"""
    if settings.INTERNAL_API_KEY and x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid internal key")
    
    run_morning_digest()
    return {"status": "digest job completed"}