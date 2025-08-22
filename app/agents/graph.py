from typing import Dict, Any
from .nodes import retrieve_and_cite, synthesize_answer, maybe_refuse, try_form_fill

def run_answer_pipeline(question: str, top_k: int = 5) -> Dict[str, Any]:
    hits, cites, top_score, coverage_tokens = retrieve_and_cite(question, k=top_k)
    refused = maybe_refuse(top_score, coverage_tokens)
    if refused:
        return {
            "answer": "I don't have enough grounded evidence to answer confidently. Please consult the source policy or narrow the question.",
            "citations": [c.model_dump() for c in cites],
            "metrics": {"top_score": top_score, "coverage_tokens": coverage_tokens, "refused": True},
        }
    answer = synthesize_answer(question, cites)
    return {"answer": answer, "citations": [c.model_dump() for c in cites], "metrics": {"top_score": top_score, "coverage_tokens": coverage_tokens, "refused": False}}

def run_form_pipeline(question: str, user_ctx: dict | None) -> Dict[str, Any]:
    out = try_form_fill(question, user_ctx)
    if not out:
        return run_answer_pipeline(question)
    form_type, data = out
    return {"form_type": form_type, "data": data, "requires_approval": True}
