from typing import List, Dict, Any, Tuple
from ..retrieval.vectorstore import VectorStore
from ..utils.text import truncate, needs_refusal
from ..utils.tracing import span
from ..schemas.api import Citation
from ..config import settings

from openai import OpenAI
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_embedding_fn():
    def _embed(texts: List[str]) -> List[List[float]]:
        resp = client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=texts
        )
        return [d.embedding for d in resp.data]
    return _embed

def build_vectorstore() -> VectorStore:
    return VectorStore(embedding_fn=get_embedding_fn())

def retrieve_and_cite(question: str, k: int = 5) -> Tuple[List[Dict[str, Any]], List[Citation], float, int]:
    with span("retrieve"):
        vs = build_vectorstore()
        hits = vs.search(question, k=k)
    citations: List[Citation] = []
    top_score = 0.0
    coverage_tokens = 0
    for h in hits:
        citations.append(Citation(
            doc_id=h["document_id"],
            title=h.get("heading") or h.get("source_uri") or "Document",
            snippet=truncate(h["text"], 300),
            source_uri=h.get("source_uri")
        ))
        top_score = max(top_score, float(h.get("score", 0.0)))
        coverage_tokens += len(h.get("text","").split())
    return hits, citations, top_score, coverage_tokens

def synthesize_answer(question: str, citations: List[Citation]) -> str:
    context_blocks = []
    for c in citations:
        context_blocks.append(f"[{c.title}] {c.snippet}")
    context = "\n---\n".join(context_blocks[:5]) if context_blocks else "No context."
    sys = (
        "You are a strict policy assistant. Use ONLY the provided context. "
        "Cite the source in brackets like [Doc Title], and refuse if insufficient evidence."
    )
    prompt = (
        f"User question: {question}\n"
        f"Context:\n{context}\n"
        "Answer with short paragraphs and bullet points where helpful. "
        "If you are unsure, say you cannot answer confidently and suggest next steps."
    )
    with span("llm.answer"):
        resp = client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2
        )
    return resp.choices[0].message.content.strip()

def maybe_refuse(top_score: float, coverage_tokens: int) -> bool:
    return needs_refusal(top_score, coverage_tokens)

def try_form_fill(question: str, user_ctx: dict | None) -> Tuple[str, dict] | None:
    q = question.lower()
    if "security exception" in q or "byod" in q or "personal mac" in q:
        from ..schemas.forms import SecurityExceptionRequest
        data = {
            "employee_id": (user_ctx or {}).get("employee_id", "E123"),
            "department": (user_ctx or {}).get("department", "Engineering"),
            "device_type": "Mac",
            "justification": "Personal Mac needed for Python dev per policy constraints.",
            "duration_days": 30,
            "data_sensitivity": "Medium"
        }
        return "SecurityExceptionRequest", SecurityExceptionRequest(**data).model_dump()
    if "pto" in q or "vacation" in q or "time off" in q:
        from ..schemas.forms import PTORequest
        data = {
            "employee_id": (user_ctx or {}).get("employee_id", "E123"),
            "manager_email": (user_ctx or {}).get("manager_email", "manager@example.com"),
            "days": 3,
            "reason": "Personal leave."
        }
        return "PTORequest", PTORequest(**data).model_dump()
    return None
