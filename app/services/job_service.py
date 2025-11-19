from __future__ import annotations

from typing import Iterable, List

from sqlalchemy.orm import Session

from .. import models
from ..providers.indeed import IndeedProvider
from ..providers.linkedin import LinkedInProvider
from ..providers.naukri import NaukriProvider
from ..rag.job_indexer import index_jobs
from ..rag.matcher import match_jobs_for_user

PROVIDERS = {
    "linkedin": LinkedInProvider(),
    "indeed": IndeedProvider(),
    "naukri": NaukriProvider(),
}


def _get_or_create_source(db: Session, provider_name: str) -> models.JobSource:
    source = db.query(models.JobSource).filter(models.JobSource.name == provider_name).first()
    if not source:
        source = models.JobSource(name=provider_name, base_url=f"https://{provider_name}.example")
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def fetch_jobs_from_all_providers(preferences: models.JobPreference | None) -> List[tuple[str, list[dict]]]:
    if preferences and preferences.providers_enabled:
        enabled = [name.strip() for name in preferences.providers_enabled.split(",") if name.strip()]
    else:
        enabled = list(PROVIDERS.keys())
    jobs_by_provider: List[tuple[str, list[dict]]] = []
    pref_dict = preferences.__dict__ if preferences else {}
    for name in enabled:
        provider = PROVIDERS.get(name.strip())
        if not provider:
            continue
        jobs = provider.search_jobs(pref_dict)
        jobs_by_provider.append((name, jobs))
    return jobs_by_provider


def upsert_job_postings_into_db(db: Session, provider_name: str, jobs: Iterable[dict]) -> list[models.JobPosting]:
    source = _get_or_create_source(db, provider_name)
    indexed = index_jobs(db, jobs, source)
    return indexed


def index_jobs_into_rag(db: Session, jobs: list[models.JobPosting]):
    # Already handled inside index_jobs via add_vector; placeholder for future enhancements
    return jobs


def run_matching_for_user(db: Session, user: models.User, jobs: list[models.JobPosting]):
    return match_jobs_for_user(db, user, jobs)
