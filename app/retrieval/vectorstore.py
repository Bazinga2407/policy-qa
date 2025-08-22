import os, json, numpy as np
from typing import List, Dict, Any
import faiss

from ..config import settings
from ..db import get_chunks_by_ids

INDEX_PATH = os.path.join(settings.STORAGE_DIR, "index.faiss")
MAP_PATH = os.path.join(settings.STORAGE_DIR, "chunk_map.json")

class VectorStore:
    def __init__(self, embedding_fn):
        self.embedding_fn = embedding_fn
        self.index = None
        self.id_map: List[str] = []
        if os.path.exists(INDEX_PATH) and os.path.exists(MAP_PATH):
            self._load()

    def _save(self):
        faiss.write_index(self.index, INDEX_PATH)
        with open(MAP_PATH, "w", encoding="utf-8") as f:
            json.dump(self.id_map, f)

    def _load(self):
        self.index = faiss.read_index(INDEX_PATH)
        with open(MAP_PATH, "r", encoding="utf-8") as f:
            self.id_map = json.load(f)

    def _ensure(self, dim: int):
        if self.index is None:
            self.index = faiss.IndexFlatIP(dim)

    def add_chunks(self, rows: List[Dict[str, Any]]) -> List[int]:
        texts = [r["text"] for r in rows]
        embs = np.array(self.embedding_fn(texts), dtype="float32")
        faiss.normalize_L2(embs)
        self._ensure(embs.shape[1])
        start_id = len(self.id_map)
        self.index.add(embs)
        for i, r in enumerate(rows):
            self.id_map.append(r["id"])
            r["faiss_id"] = start_id + i
        self._save()
        return list(range(start_id, start_id + len(rows)))

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        if self.index is None or len(self.id_map) == 0:
            return []
        q = np.array(self.embedding_fn([query]), dtype="float32")
        faiss.normalize_L2(q)
        D, I = self.index.search(q, k)
        out = []
        for score, idx in zip(D[0].tolist(), I[0].tolist()):
            if idx == -1: continue
            chunk_id = self.id_map[idx]
            out.append({"chunk_id": chunk_id, "score": float(score)})
        chunk_rows = get_chunks_by_ids([o["chunk_id"] for o in out])
        row_map = {r["id"]: r for r in chunk_rows}
        for o in out:
            r = row_map.get(o["chunk_id"])
            if r:
                o.update(r)
        return out
