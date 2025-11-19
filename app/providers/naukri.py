from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .base import JobProvider

DATA_PATH = Path("data/naukri_jobs.json")


class NaukriProvider(JobProvider):
    name = "naukri"

    def search_jobs(self, preferences: dict, page: int = 1) -> List[dict]:  # noqa: ARG002
        if DATA_PATH.exists():
            with DATA_PATH.open() as f:
                jobs = json.load(f)
        else:
            jobs = [
                {
                    "external_job_id": "na-1",
                    "title": "Data Scientist",
                    "company": "Naukri Mock",
                    "location": "Bengaluru, India",
                    "url": "https://naukri.example/jobs/1",
                    "description": "Analyze data and build ML models.",
                    "posted_at": None,
                }
            ]
        return jobs
