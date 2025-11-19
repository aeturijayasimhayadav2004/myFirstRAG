from __future__ import annotations

from datetime import datetime

from .. import models


def build_match_explanation(user: models.User, job: models.JobPosting, similarity: float | str):
    similarity = float(similarity)
    reason = f"Resume for {user.email} matches {job.title} at {job.company} with similarity {similarity:.2f}."
    cover_letter = f"Dear {job.company},\n\nI am excited to apply for the {job.title} role. My experience aligns with your needs, and I would love to contribute to your team.\n\nBest regards,\n{user.email}"
    return {"reason": reason, "cover_letter": cover_letter}
