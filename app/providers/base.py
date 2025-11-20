from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class JobProvider(ABC):
    name: str

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    @abstractmethod
    def search_jobs(self, preferences: dict, page: int = 1) -> List[dict]:
        raise NotImplementedError
