def truncate(s: str, n: int = 350) -> str:
    s = s.strip().replace("\n", " ")
    return s if len(s) <= n else s[:n] + "..."

def needs_refusal(similarity_floor: float, coverage_tokens: int, min_floor: float = 0.18, min_coverage: int = 80) -> bool:
    return similarity_floor < min_floor or coverage_tokens < min_coverage
