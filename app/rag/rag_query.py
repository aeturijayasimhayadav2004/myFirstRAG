from __future__ import annotations

from .. import models


def _matched_skills(user: models.User, job: models.JobPosting):
    job_text = f"{job.title or ''} {job.description or ''}".lower()
    overlaps = [skill.name for skill in user.skills if skill.name and skill.name.lower() in job_text]
    return overlaps[:5]


def build_match_explanation(user: models.User, job: models.JobPosting, similarity: float | str):
    similarity = float(similarity)
    skills = _matched_skills(user, job)
    skill_text = ", ".join(skills) if skills else "your core skills"
    preference_clause = "remote" if job.location and "remote" in job.location.lower() else (job.location or "the listed location")
    reason = (
        f"Similarity {similarity:.2f} because {skill_text} align with the {job.title} role at {job.company} in {preference_clause}."
    )
    cover_letter = (
        f"Dear {job.company},\n\nI am excited to apply for the {job.title} position. "
        f"My experience with {skill_text} maps closely to your requirements, and I am eager to contribute from day one. "
        f"I welcome the opportunity to discuss how I can support your team.\n\nBest regards,\n{user.email}"
    )
    return {"reason": reason, "cover_letter": cover_letter}
