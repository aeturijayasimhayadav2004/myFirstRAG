from datetime import datetime
from typing import Iterable

from sqlalchemy.orm import Session

from .. import models
from .embeddings import add_vector, blend_vectors


def index_jobs(db: Session, jobs: Iterable[dict], source: models.JobSource) -> list[models.JobPosting]:
    indexed_jobs: list[models.JobPosting] = []
    for job in jobs:
        existing = (
            db.query(models.JobPosting)
            .filter(models.JobPosting.external_job_id == job["external_job_id"], models.JobPosting.source_id == source.id)
            .first()
        )
        vector = blend_vectors(
            [
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
                job.get("description", ""),
            ]
        )
        posted_at_value = job.get("posted_at")
        if isinstance(posted_at_value, str):
            try:
                posted_at_value = datetime.fromisoformat(posted_at_value)
            except ValueError:
                posted_at_value = datetime.utcnow()
        elif not posted_at_value:
            posted_at_value = datetime.utcnow()
        if existing:
            existing.title = job.get("title")
            existing.company = job.get("company")
            existing.location = job.get("location")
            existing.url = job.get("url")
            existing.description = job.get("description")
            existing.raw_data = job
            existing.embedding_vector = vector.tobytes()
            existing.posted_at = posted_at_value
            db.add(existing)
            db.commit()
            db.refresh(existing)
            add_vector(existing.id, vector)
            indexed_jobs.append(existing)
            continue
        posting = models.JobPosting(
            source_id=source.id,
            external_job_id=job["external_job_id"],
            title=job.get("title"),
            company=job.get("company"),
            location=job.get("location"),
            url=job.get("url"),
            description=job.get("description"),
            raw_data=job,
            embedding_vector=vector.tobytes(),
            posted_at=posted_at_value,
        )
        db.add(posting)
        db.commit()
        db.refresh(posting)
        add_vector(posting.id, vector)
        indexed_jobs.append(posting)
    return indexed_jobs
