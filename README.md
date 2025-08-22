# Policy Q&A with Provenance & Evals (Agentic RAG)

A production-style, agentic RAG service that answers HR/Legal/Security questions with **citations**, performs **form-filling** via typed schemas, and enforces **refusal/redaction** when evidence is insufficient. Includes ingestion, retrieval, evals, tests, Docker, and CI-ready structure.

> ⚠️ You need an OpenAI API key to run embedding and chat calls.

## Quickstart

```bash
cp .env.example .env
# Edit .env with your OpenAI key
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
# Open http://localhost:8000/docs
# Use header: X-API-Key: dev-secret
# 1) POST /ingest with files from data/sample/
# 2) POST /query  (or /query?mode=form)
````

### With Docker

```bash
cp .env.example .env
docker compose up --build
# API at http://localhost:8000/docs
```

## Endpoints

- `POST /ingest` — upload files (PDF/DOCX/HTML/TXT). Returns doc IDs and chunk stats.
- `POST /query` — ask a question. Returns `{answer, citations[], metrics}`.
- `POST /query?mode=form` — attempts typed form fill (e.g., security exception request).
- `GET /docs/{document_id}` — metadata and chunk preview for a document.
- `POST /eval/run` — runs offline eval cases in `evals/cases.yaml`.

## Storage

- SQLite DB: `storage/meta.db` (documents & chunks)
- FAISS index: `storage/index.faiss`
- Mapping JSON: `storage/chunk_map.json` (faiss_id → chunk_id)

## Tests

```bash
pytest -q
```
