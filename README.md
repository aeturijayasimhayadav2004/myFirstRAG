# RAG Job Matcher

An experimental Retrieval Augmented Generation (RAG) demo that ingests resumes, fetches mock job postings from LinkedIn/Indeed/Naukri providers, runs similarity-based matching, and simulates auto-applications. Built with FastAPI, SQLAlchemy, and a lightweight FAISS-compatible vector index.

## Features
- Email/password auth with JWT cookies.
- Resume ingestion + fake embeddings stored in SQLite.
- Mock job providers (LinkedIn, Indeed, Naukri) that read JSON fixtures in `data/`.
- FAISS (or in-memory) similarity search, rule-based filters, and match explanations.
- Background scheduler that periodically fetches jobs, indexes them, and auto applies within preference limits.
- Minimal dashboard UI rendered with Jinja2 templates.

## Getting Started

### 1. Install Dependencies
Run all commands from the repository root (the folder that contains this README).

```bash
cd myFirstRAG                     # only if you are not already in the repo root
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the App Locally

```bash
uvicorn app.main:app --reload     # exposes http://127.0.0.1:8000
```

For a deployment-like command, pin the host/port explicitly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Use the App
1. Register via API:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "changeme"}'
```
2. Visit `http://localhost:8000/` to log in with your credentials.
3. Upload a resume, configure preferences, explore matches, and inspect simulated applications. The background scheduler will st
art automatically once the FastAPI app is running.

## Mock Data
JSON fixtures located in `data/` power the providers:
- `data/linkedin_jobs.json`
- `data/indeed_jobs.json`
- `data/naukri_jobs.json`

Feel free to edit or extend them to experiment with new postings.

## Notes
- Providers are **mock implementations**. No real LinkedIn/Indeed/Naukri API calls are made.
- Embeddings are deterministic hash-based vectors so the project runs offline without heavy dependencies.
- The background scheduler uses APScheduler with an in-process job. Adjust intervals via `app/config.py`.
