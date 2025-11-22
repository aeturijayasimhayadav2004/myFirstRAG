from __future__ import annotations

from datetime import datetime, date

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import models
from .auth import create_access_token, get_current_user, verify_password
from .config import get_settings
from .db import Base, engine, get_db
from .routes import applications, jobs, preferences, resume, users
from .services.scheduler import shutdown_scheduler, start_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RAG Job Matcher")
settings = get_settings()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # WARNING: In production, replace ["*"] with your specific frontend domain (e.g., ["https://your-app.onrender.com"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(users.router)
app.include_router(resume.router)
app.include_router(preferences.router)
app.include_router(jobs.router)
app.include_router(applications.router)


@app.on_event("startup")
def _startup():
    if settings.secret_key == "super-secret-key":
        print("WARNING: You are using the default SECRET_KEY. This is insecure for production!")
    start_scheduler()


@app.on_event("shutdown")
def _shutdown():
    shutdown_scheduler()


@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "user": None, "error": None})


@app.post("/login")
def browser_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "user": None, "error": "Invalid credentials"},
            status_code=400,
        )
    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie("access_token", token, httponly=True)
    return response


@app.get("/dashboard")
def dashboard(request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    matches = db.query(models.JobMatch).filter(models.JobMatch.user_id == current_user.id).count()
    today = date.today()
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    applications_today = (
        db.query(models.Application)
        .filter(models.Application.user_id == current_user.id, models.Application.submitted_at >= today_start)
        .count()
    )
    resume_uploaded = (
        db.query(models.Resume)
        .filter(models.Resume.user_id == current_user.id)
        .first()
        is not None
    )
    stats = {
        "matches": matches,
        "applications_today": applications_today,
        "resume_uploaded": resume_uploaded,
    }
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user, "stats": stats})


@app.get("/api/dashboard")
def api_dashboard(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    matches = db.query(models.JobMatch).filter(models.JobMatch.user_id == current_user.id).count()
    today = date.today()
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    applications_today = (
        db.query(models.Application)
        .filter(models.Application.user_id == current_user.id, models.Application.submitted_at >= today_start)
        .count()
    )
    resume_uploaded = (
        db.query(models.Resume)
        .filter(models.Resume.user_id == current_user.id)
        .first()
        is not None
    )
    return {
        "matches": matches,
        "applications_today": applications_today,
        "resume_uploaded": resume_uploaded,
        "user_email": current_user.email
    }
