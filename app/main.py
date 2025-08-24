import os, uuid, datetime
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
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

app = FastAPI(
    title="Policy Q&A with Provenance & Evals",
    description="AI-powered document analysis with citations and form filling capabilities",
    version="1.0.0"
)

# Enhanced CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000",
        "http://localhost:8000",  # Production
        "*"  # Allow all origins - restrict this in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and storage
init_db()
os.makedirs(settings.STORAGE_DIR, exist_ok=True)

# Serve React static files (production build)
frontend_path = Path(__file__).parent.parent / "frontend" / "build"
if frontend_path.exists():
    # Mount static files (CSS, JS, images)
    app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.utcnow().isoformat()}

# API Routes (your existing endpoints)
@app.post("/ingest", response_model=IngestResponse, dependencies=[Depends(require_auth)])
async def ingest(files: List[UploadFile] = File(...), title: str = Form(None)):
    """
    Enhanced ingest endpoint to handle multiple files from React frontend
    """
    results = []
    total_chunks = 0
    
    for file in files:
        data = await file.read()
        name = file.filename or title or "document"
        ext = (name.split(".")[-1] or "").lower()
        
        # Parse based on file extension
        if ext in ["pdf"]:
            text = parse_pdf(data)
        elif ext in ["docx"]:
            text = parse_docx(data)
        elif ext in ["html", "htm"]:
            text = parse_html(data)
        elif ext in ["txt", "md"]:
            text = parse_txt(data)
        else:
            text = parse_txt(data)

        document_id = str(uuid.uuid4())
        file_title = title or name
        
        # Insert document metadata
        insert_document({
            "id": document_id,
            "title": file_title,
            "source_uri": name,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "tags": "",
        })
        
        # Chunk and vectorize text
        chunks = chunk_text(text, max_tokens=300, overlap_tokens=40)
        rows = attach_metadata(chunks, document_id=document_id, title=file_title, source_uri=name)

        vs = VectorStore(embedding_fn=get_embedding_fn())
        vs.add_chunks(rows)
        insert_chunks(rows)
        
        results.append({
            "document_id": document_id,
            "title": file_title,
            "num_chunks": len(rows)
        })
        total_chunks += len(rows)
    
    # Return response compatible with React frontend
    return {
        "documents": results,
        "total_files": len(files),
        "total_chunks": total_chunks,
        "message": f"Successfully processed {len(files)} file(s)"
    }

@app.get("/docs/{doc_id}", dependencies=[Depends(require_auth)])
def get_doc(doc_id: str):
    """Get document metadata and chunk preview"""
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    chunks = get_chunks_by_doc(doc_id, limit=30)
    return {"document": doc, "chunks_preview": chunks}

@app.get("/documents", dependencies=[Depends(require_auth)])
def list_documents():
    """List all documents - new endpoint for React frontend"""
    try:
        # You might need to implement this in your db module
        # For now, return empty list
        return {"documents": []}
    except Exception as e:
        return {"documents": [], "error": str(e)}

@app.post("/query", response_model=AnswerResponse, dependencies=[Depends(require_auth)])
def query(req: QueryRequest):
    """
    Enhanced query endpoint with better error handling for React frontend
    """
    try:
        if req.mode == "form":
            res = run_form_pipeline(req.question, req.user_context)
            if "form_type" in res:
                return AnswerResponse(
                    answer=f"Generated form `{res['form_type']}` (requires approval).",
                    citations=[],
                    metrics={
                        "form_type": res["form_type"], 
                        "requires_approval": res["requires_approval"],
                        "processing_time": res.get("processing_time", 0)
                    }
                )
        
        res = run_answer_pipeline(req.question, top_k=req.top_k)
        return AnswerResponse(
            answer=res["answer"], 
            citations=res["citations"], 
            metrics=res["metrics"]
        )
    except Exception as e:
        return AnswerResponse(
            answer=f"Error processing query: {str(e)}",
            citations=[],
            metrics={"error": True, "error_message": str(e)}
        )

@app.post("/eval/run", dependencies=[Depends(require_auth)])
def run_eval():
    """Run evaluation suite"""
    try:
        from evals.runner import run_all as _run
        result = _run()
        return {
            "status": "completed",
            "results": result,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

# React Frontend Routes (Must be last!)

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    favicon_path = frontend_path / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(str(favicon_path))
    raise HTTPException(status_code=404)

@app.get("/manifest.json")
async def manifest():
    """Serve manifest.json"""
    manifest_path = frontend_path / "manifest.json"
    if manifest_path.exists():
        return FileResponse(str(manifest_path))
    raise HTTPException(status_code=404)

# Catch-all route for React Router (SPA support)
@app.get("/{catchall:path}")
async def serve_react_app(catchall: str):
    """
    Serve React app for all non-API routes
    This enables client-side routing
    """
    # Don't serve React for API routes
    if catchall.startswith(("api/", "docs", "openapi.json", "redoc")):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Serve React index.html for all other routes
    if frontend_path.exists():
        return FileResponse(str(frontend_path / "index.html"))
    else:
        # Fallback if frontend not built
        return {
            "message": "Policy Q&A API - Frontend not available", 
            "api_docs": "/docs",
            "health": "/health"
        }

# Root route serves React app
@app.get("/")
async def serve_root():
    """Serve React app at root or API info if frontend not available"""
    if frontend_path.exists():
        return FileResponse(str(frontend_path / "index.html"))
    else:
        return {
            "message": "Policy Q&A API", 
            "docs": "/docs",
            "health": "/health",
            "version": "1.0.0"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)