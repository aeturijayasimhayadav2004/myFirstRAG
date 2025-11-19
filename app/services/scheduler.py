from __future__ import annotations

from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from .. import models
from ..config import get_settings
from ..db import SessionLocal
from . import job_service, application_service

settings = get_settings()
scheduler = BackgroundScheduler()


def _job_runner():
    db: Session = SessionLocal()
    try:
        users = db.query(models.User).all()
        for user in users:
            preferences = user.preferences
            jobs_by_provider = job_service.fetch_jobs_from_all_providers(preferences)
            all_new_jobs = []
            for provider_name, jobs in jobs_by_provider:
                postings = job_service.upsert_job_postings_into_db(db, provider_name, jobs)
                all_new_jobs.extend(postings)
            matches = job_service.run_matching_for_user(db, user, all_new_jobs)
            if preferences and preferences.auto_apply_enabled:
                today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                existing_today = (
                    db.query(models.Application)
                    .filter(
                        models.Application.user_id == user.id,
                        models.Application.submitted_at >= today_start,
                    )
                    .count()
                )
                remaining = (preferences.max_applications_per_day or 0) - existing_today
                for match in matches[: max(0, remaining)]:
                    application_service.auto_apply_for_match(db, match)
    finally:
        db.close()


def start_scheduler():
    if scheduler.running:
        return
    scheduler.add_job(_job_runner, "interval", seconds=settings.scheduler_interval_seconds, id="job-runner", replace_existing=True)
    scheduler.start()
