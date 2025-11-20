from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .. import models
from ..auth import get_current_user
from ..db import get_db

router = APIRouter(prefix="/applications", tags=["applications"])
templates = Jinja2Templates(directory="app/templates")


def _fetch_applications(current_user: models.User, db: Session):
    query = (
        db.query(models.Application, models.JobPosting)
        .join(models.JobPosting, models.JobPosting.id == models.Application.job_id)
        .filter(models.Application.user_id == current_user.id)
        .order_by(models.Application.submitted_at.desc().nullslast())
    )
    results = []
    for app_row, job in query.all():
        results.append(
            {
                "id": app_row.id,
                "job_id": app_row.job_id,
                "status": app_row.status,
                "submitted_at": app_row.submitted_at,
                "error_message": app_row.error_message,
                "job_title": job.title,
            }
        )
    return results


@router.get("")
def list_applications(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = _fetch_applications(current_user, db)
    return templates.TemplateResponse("applications.html", {"request": request, "user": current_user, "applications": data})


@router.get("/json")
def list_applications_json(
    current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return _fetch_applications(current_user, db)
