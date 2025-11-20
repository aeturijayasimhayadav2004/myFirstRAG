from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .base import JobProvider

DATA_PATH = Path("data/linkedin_jobs.json")


class LinkedInProvider(JobProvider):
    name = "linkedin"

    def search_jobs(self, preferences: dict, page: int = 1) -> List[dict]:  # noqa: ARG002
        # If an API key is supplied, the provider can be swapped to a real client without
        # breaking the rest of the codebase. For now, we keep the mock data for stability
        # while allowing deployment environments to inject credentials.
        if DATA_PATH.exists():
            with DATA_PATH.open() as f:
                jobs = json.load(f)
        else:
            jobs = [
                {
                    "external_job_id": "li-1",
                    "title": "Python Backend Engineer",
                    "company": "LinkedIn Mock",
                    "location": "Remote",
                    "url": "https://linkedin.example/jobs/1",
                    "description": "Build APIs using FastAPI and RAG.",
                    "posted_at": None,
                }
            ]
        return jobs
