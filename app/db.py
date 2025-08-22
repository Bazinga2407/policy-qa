import sqlite3
import os
from typing import Iterable, Dict, Any
from .config import settings

DB_PATH = os.path.join(settings.STORAGE_DIR, "meta.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript(
        '''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            title TEXT,
            source_uri TEXT,
            created_at TEXT,
            tags TEXT
        );
        CREATE TABLE IF NOT EXISTS chunks (
            id TEXT PRIMARY KEY,
            document_id TEXT,
            text TEXT,
            page INTEGER,
            heading TEXT,
            source_uri TEXT,
            faiss_id INTEGER,
            FOREIGN KEY(document_id) REFERENCES documents(id)
        );
        '''
    )
    conn.commit()
    conn.close()

def insert_document(doc: Dict[str, Any]):
    conn = get_conn()
    conn.execute(
        "INSERT INTO documents (id, title, source_uri, created_at, tags) VALUES (?, ?, ?, ?, ?)",
        (doc["id"], doc["title"], doc.get("source_uri",""), doc["created_at"], doc.get("tags","")),
    )
    conn.commit()
    conn.close()

def insert_chunks(rows: Iterable[Dict[str, Any]]):
    conn = get_conn()
    conn.executemany(
        "INSERT INTO chunks (id, document_id, text, page, heading, source_uri, faiss_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        [(r["id"], r["document_id"], r["text"], r["page"], r["heading"], r.get("source_uri",""), r["faiss_id"]) for r in rows]
    )
    conn.commit()
    conn.close()

def get_document(doc_id: str):
    conn = get_conn()
    row = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_chunks_by_doc(doc_id: str, limit: int = 50):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM chunks WHERE document_id=? LIMIT ?", (doc_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_chunks_by_ids(ids: list[str]) -> list[dict]:
    if not ids:
        return []
    conn = get_conn()
    q = "SELECT * FROM chunks WHERE id IN (%s)" % (",".join(["?"]*len(ids)))
    rows = conn.execute(q, ids).fetchall()
    conn.close()
    return [dict(r) for r in rows]
