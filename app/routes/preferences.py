from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..db import get_db

router = APIRouter(prefix="/preferences", tags=["preferences"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
def get_preferences(request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    prefs = db.query(models.JobPreference).filter(models.JobPreference.user_id == current_user.id).first()
    return templates.TemplateResponse("preferences.html", {"request": request, "user": current_user, "prefs": prefs})


@router.post("")
def upsert_preferences(
    request: Request,
    preferred_titles: str | None = Form(None),
    locations: str | None = Form(None),
    remote_only: str | None = Form(None),
    min_salary: int | None = Form(None),
    job_type: str | None = Form(None),
    auto_apply_enabled: str | None = Form(None),
    max_applications_per_day: int | None = Form(3),
    providers_enabled: str | None = Form(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prefs = db.query(models.JobPreference).filter(models.JobPreference.user_id == current_user.id).first()
    values = schemas.JobPreferenceIn(
        preferred_titles=preferred_titles,
        locations=locations,
        remote_only=bool(remote_only),
        min_salary=min_salary,
        job_type=job_type,
        auto_apply_enabled=bool(auto_apply_enabled),
        max_applications_per_day=max_applications_per_day,
        providers_enabled=providers_enabled,
    )
    if prefs:
        for field, value in values.dict().items():
            setattr(prefs, field, value)
    else:
        prefs = models.JobPreference(user_id=current_user.id, **values.dict())
        db.add(prefs)
    db.commit()
    return RedirectResponse(url="/preferences", status_code=303)


@router.get("/json", response_model=schemas.JobPreferenceOut | None)
def get_preferences_json(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.JobPreference).filter(models.JobPreference.user_id == current_user.id).first()
