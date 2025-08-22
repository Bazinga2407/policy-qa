from typing import List, Dict, Any, Iterable

def simple_token_len(s: str) -> int:
    return max(1, len(s.split()))

def chunk_text(text: str, max_tokens: int = 300, overlap_tokens: int = 40) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        j = min(len(words), i + max_tokens)
        chunk = " ".join(words[i:j])
        chunks.append(chunk.strip())
        if j == len(words): break
        i = j - overlap_tokens
        if i < 0: i = 0
    return [c for c in chunks if c.strip()]

def attach_metadata(chunks: List[str], document_id: str, title: str, source_uri: str = "") -> List[Dict[str, Any]]:
    rows = []
    for idx, c in enumerate(chunks):
        rows.append({
            "id": f"{document_id}_{idx}",
            "document_id": document_id,
            "text": c,
            "page": None,
            "heading": None,
            "source_uri": source_uri,
        })
    return rows
