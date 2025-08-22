import yaml, time
from pathlib import Path
from typing import Dict, Any
from app.agents.graph import run_answer_pipeline

def run_all() -> Dict[str, Any]:
    cases = yaml.safe_load(Path("evals/cases.yaml").read_text())["cases"]
    results = []
    start = time.time()
    for c in cases:
        res = run_answer_pipeline(c["question"], top_k=5)
        answer = res["answer"].lower()
        ok = any(kw.lower() in answer for kw in c.get("must_include_any", []))
        results.append({"id": c["id"], "ok": ok, "metrics": res.get("metrics", {}), "answer": res["answer"][:500]})
    dur = (time.time() - start) * 1000
    p_ok = sum(1 for r in results if r["ok"]) / max(1,len(results))
    return {"count": len(results), "pass_rate": p_ok, "duration_ms": dur, "results": results}
