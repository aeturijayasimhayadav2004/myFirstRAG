from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session

from .. import models


def create_application_for_match(db: Session, match: models.JobMatch) -> models.Application:
    existing = (
        db.query(models.Application)
        .filter(models.Application.user_id == match.user_id, models.Application.job_id == match.job_id)
        .first()
    )
    if existing:
        return existing
    application = models.Application(
        user_id=match.user_id,
        job_id=match.job_id,
        status="PENDING_SUBMISSION",
        application_payload={"match_id": match.id},
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def simulate_submission(application: models.Application, provider_name: str) -> tuple[str, str | None]:
    if provider_name == "linkedin":
        return "SUBMITTED", None
    if provider_name == "indeed":
        return "MANUAL_REQUIRED", "Provider requires manual apply"
    return "SUBMITTED", None


def auto_apply_for_match(db: Session, match: models.JobMatch):
    application = create_application_for_match(db, match)
    provider_name = match.job.source.name if match.job and match.job.source else "unknown"
    status, error = simulate_submission(application, provider_name)
    application.status = status
    application.error_message = error
    if status == "SUBMITTED":
        application.submitted_at = datetime.utcnow()
    db.add(application)
    db.commit()
    db.refresh(application)
    return application
