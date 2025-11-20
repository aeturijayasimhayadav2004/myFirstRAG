from __future__ import annotations

from datetime import datetime
import json
from typing import Iterable, List

import numpy as np
from sqlalchemy.orm import Session

from .. import models
from .embeddings import blend_vectors


SIMILARITY_THRESHOLD = 0.7


def _parse_list_field(value: str | None) -> List[str]:
    if not value:
        return []
    value = value.strip()
    if value.startswith("["):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item) for item in parsed if item]
        except json.JSONDecodeError:
            pass
    return [item.strip() for item in value.split(",") if item.strip()]


def _build_profile_vector(user: models.User, resume_vec: np.ndarray) -> np.ndarray:
    skill_segments = [skill.name for skill in user.skills]
    prefs = user.preferences
    preference_terms: list[str] = []
    if prefs:
        preference_terms.extend(_parse_list_field(prefs.preferred_titles))
        preference_terms.extend(_parse_list_field(prefs.locations))
        if prefs.job_type:
            preference_terms.append(prefs.job_type)
    segments = [" ".join(skill_segments), " ".join(preference_terms)]
    blended = blend_vectors(segments)
    combined = np.mean(np.stack([resume_vec, blended], axis=0), axis=0)
    norm = np.linalg.norm(combined) or 1.0
    return combined / norm


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
    profile_vec = _build_profile_vector(user, resume_vec)
    prefs = user.preferences
    matched = []
    for job in jobs:
        base_vec = (
            np.frombuffer(job.embedding_vector, dtype="float32")
            if job.embedding_vector
            else blend_vectors([job.description or "", job.title or "", job.company or ""])
        )
        context_vec = blend_vectors([job.title or "", job.company or "", job.location or ""])
        job_vec = np.mean(np.stack([base_vec, context_vec], axis=0), axis=0)
        sim = cosine_similarity(profile_vec, job_vec)
        if sim < SIMILARITY_THRESHOLD:
            continue
        if prefs:
            if prefs.remote_only and "remote" not in (job.location or "").lower():
                continue
            if prefs.job_type and prefs.job_type.lower() not in (job.description or "").lower():
                continue
            preferred_locations = _parse_list_field(prefs.locations)
            if preferred_locations:
                job_loc = (job.location or "").lower()
                if job_loc and not any(loc.lower() in job_loc for loc in preferred_locations):
                    continue
            enabled_providers = _parse_list_field(prefs.providers_enabled)
            if enabled_providers and job.source and job.source.name not in enabled_providers:
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
