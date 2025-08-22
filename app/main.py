import os, uuid, datetime
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .config import settings
from .db import init_db, insert_document, insert_chunks, get_document, get_chunks_by_doc
from .ingest.parser import parse_pdf, parse_docx, parse_html, parse_txt
from .ingest.chunker import chunk_text, attach_metadata
from .retrieval.vectorstore import VectorStore
from .schemas.api import IngestResponse, QueryRequest, AnswerResponse
from .agents.graph import run_answer_pipeline, run_form_pipeline
from .agents.nodes import get_embedding_fn
from .utils.security import require_auth

load_dotenv()
app = FastAPI(title="Policy Q&A with Provenance & Evals")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
os.makedirs(settings.STORAGE_DIR, exist_ok=True)

@app.post("/ingest", response_model=IngestResponse, dependencies=[Depends(require_auth)])
async def ingest(file: UploadFile = File(...), title: str = Form(None)):
    data = await file.read()
    name = file.filename or title or "document"
    ext = (name.split(".")[-1] or "").lower()
    if ext in ["pdf"]:
        text = parse_pdf(data)
    elif ext in ["docx"]:
        text = parse_docx(data)
    elif ext in ["html","htm"]:
        text = parse_html(data)
    elif ext in ["txt","md"]:
        text = parse_txt(data)
    else:
        text = parse_txt(data)

    document_id = str(uuid.uuid4())
    title = title or name
    insert_document({
        "id": document_id,
        "title": title,
        "source_uri": name,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "tags": "",
    })
    chunks = chunk_text(text, max_tokens=300, overlap_tokens=40)
    rows = attach_metadata(chunks, document_id=document_id, title=title, source_uri=name)

    vs = VectorStore(embedding_fn=get_embedding_fn())
    vs.add_chunks(rows)
    insert_chunks(rows)

    return IngestResponse(document_id=document_id, title=title, num_chunks=len(rows))

@app.get("/docs/{doc_id}", dependencies=[Depends(require_auth)])
def get_doc(doc_id: str):
    doc = get_document(doc_id)
    if not doc:
        return {"error": "not found"}
    chunks = get_chunks_by_doc(doc_id, limit=30)
    return {"document": doc, "chunks_preview": chunks}

@app.post("/query", response_model=AnswerResponse, dependencies=[Depends(require_auth)])
def query(req: QueryRequest):
    if req.mode == "form":
        res = run_form_pipeline(req.question, req.user_context)
        if "form_type" in res:
            return AnswerResponse(
                answer=f"Generated form `{res['form_type']}` (requires approval).",
                citations=[],
                metrics={"form": res["form_type"], "requires_approval": res["requires_approval"]}
            )
    res = run_answer_pipeline(req.question, top_k=req.top_k)
    return AnswerResponse(answer=res["answer"], citations=res["citations"], metrics=res["metrics"])

@app.post("/eval/run", dependencies=[Depends(require_auth)])
def run_eval():
    from evals.runner import run_all as _run
    return _run()
