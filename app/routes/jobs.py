from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .. import models
from ..auth import get_current_user
from ..db import get_db
from ..rag.rag_query import build_match_explanation

router = APIRouter(prefix="/jobs", tags=["jobs"])
templates = Jinja2Templates(directory="app/templates")


def _fetch_matches(current_user: models.User, db: Session, status: str | None = None):
    query = (
        db.query(models.JobMatch, models.JobPosting)
        .join(models.JobPosting, models.JobPosting.id == models.JobMatch.job_id)
        .filter(models.JobMatch.user_id == current_user.id)
    )
    if status:
        query = query.filter(models.JobMatch.status == status)
    matches = []
    for match, job in query.order_by(models.JobMatch.created_at.desc()).all():
        explanation = build_match_explanation(current_user, job, match.similarity_score)
        matches.append(
            {
                "id": match.id,
                "job_id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "similarity_score": float(match.similarity_score),
                "status": match.status,
                "reason": explanation["reason"],
                "cover_letter": explanation["cover_letter"],
            }
        )
    return matches


@router.get("/matches")
def list_matches(request: Request, status: str | None = None, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    matches = _fetch_matches(current_user, db, status)
    return templates.TemplateResponse("jobs.html", {"request": request, "user": current_user, "matches": matches})


@router.get("/matches/json")
def list_matches_json(status: str | None = None, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _fetch_matches(current_user, db, status)
