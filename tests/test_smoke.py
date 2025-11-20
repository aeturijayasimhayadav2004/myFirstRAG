import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.main import app


def test_app_imports():
    assert app.title == "RAG Job Matcher"
