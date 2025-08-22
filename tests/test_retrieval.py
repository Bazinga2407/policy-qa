import os, uuid, datetime
from app.db import init_db, insert_document, insert_chunks
from app.retrieval.vectorstore import VectorStore

def test_vectorstore_add_and_search(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path))
    from importlib import reload
    import app.config as cfg
    reload(cfg)
    from app.config import settings

    init_db()
    # Deterministic fake embeddings (8D)
    vs = VectorStore(embedding_fn=lambda texts: [[float(i+1) for i in range(8)]]*len(texts))
    rows = [{"id": f"doc1_{i}", "document_id":"doc1", "text": f"text {i}", "page":None, "heading":None, "source_uri":"", "faiss_id":-1} for i in range(3)]
    vs.add_chunks(rows)
    insert_document({"id":"doc1","title":"Doc","source_uri":"","created_at":datetime.datetime.utcnow().isoformat(),"tags":""})
    insert_chunks(rows)
    out = vs.search("hello", k=2)
    assert len(out) == 2
