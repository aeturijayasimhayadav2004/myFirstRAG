from __future__ import annotations

from datetime import datetime
from typing import Iterable

import numpy as np
from sqlalchemy.orm import Session

from .. import models
from .embeddings import embed_text


SIMILARITY_THRESHOLD = 0.75


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    denom = (np.linalg.norm(vec_a) * np.linalg.norm(vec_b)) or 1.0
    return float(np.dot(vec_a, vec_b) / denom)


def match_jobs_for_user(db: Session, user: models.User, jobs: Iterable[models.JobPosting]):
    resume = (
        db.query(models.Resume)
        .filter(models.Resume.user_id == user.id)
        .order_by(models.Resume.created_at.desc())
        .first()
    )
    if not resume or not resume.embedding_vector:
        return []
    resume_vec = np.frombuffer(resume.embedding_vector, dtype="float32")
    prefs = user.preferences
    matched = []
    for job in jobs:
        job_vec = (
            np.frombuffer(job.embedding_vector, dtype="float32")
            if job.embedding_vector
            else embed_text(job.description or "")
        )
        sim = cosine_similarity(resume_vec, job_vec)
        if sim < SIMILARITY_THRESHOLD:
            continue
        if prefs:
            if prefs.remote_only and "remote" not in (job.location or "").lower():
                continue
            if prefs.job_type and prefs.job_type.lower() not in (job.description or "").lower():
                continue
        existing = (
            db.query(models.JobMatch)
            .filter(models.JobMatch.user_id == user.id, models.JobMatch.job_id == job.id)
            .first()
        )
        if existing:
            existing.similarity_score = f"{sim:.4f}"
            existing.status = "MATCHED"
            existing.reason = f"Similarity {sim:.2f}"
            db.add(existing)
            matched.append(existing)
            continue
        match = models.JobMatch(
            user_id=user.id,
            job_id=job.id,
            similarity_score=f"{sim:.4f}",
            status="MATCHED",
            reason=f"Resume aligns with {job.title}",
            created_at=datetime.utcnow(),
        )
        db.add(match)
        matched.append(match)
    db.commit()
    return matched
