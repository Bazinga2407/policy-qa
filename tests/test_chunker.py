from app.ingest.chunker import chunk_text

def test_chunker_basic():
    txt = " ".join(["word"]*1200)
    chunks = chunk_text(txt, max_tokens=200, overlap_tokens=20)
    assert len(chunks) >= 5
    assert " ".join(chunks[0].split()[-20:]) == " ".join(chunks[1].split()[:20])
