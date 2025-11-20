from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .base import JobProvider

DATA_PATH = Path("data/indeed_jobs.json")


class IndeedProvider(JobProvider):
    name = "indeed"

    def search_jobs(self, preferences: dict, page: int = 1) -> List[dict]:  # noqa: ARG002
        # Ready for real API integration when api_key is configured; defaults to mock data.
        if DATA_PATH.exists():
            with DATA_PATH.open() as f:
                jobs = json.load(f)
        else:
            jobs = [
                {
                    "external_job_id": "in-1",
                    "title": "Full Stack Engineer",
                    "company": "Indeed Mock",
                    "location": "New York, NY",
                    "url": "https://indeed.example/jobs/1",
                    "description": "Work on frontend and backend systems.",
                    "posted_at": None,
                }
            ]
        return jobs
