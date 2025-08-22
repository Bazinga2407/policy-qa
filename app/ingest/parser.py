from typing import List, Tuple
from bs4 import BeautifulSoup
from pypdf import PdfReader
from docx import Document

def parse_pdf(bytes_data: bytes) -> str:
    from io import BytesIO
    reader = PdfReader(BytesIO(bytes_data))
    texts = []
    for i, page in enumerate(reader.pages):
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""
        texts.append(txt)
    return "\n".join(texts)

def parse_docx(bytes_data: bytes) -> str:
    from io import BytesIO
    doc = Document(BytesIO(bytes_data))
    paras = [p.text for p in doc.paragraphs]
    return "\n".join(paras)

def parse_html(bytes_data: bytes) -> str:
    html = bytes_data.decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script","style","noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    return text

def parse_txt(bytes_data: bytes) -> str:
    return bytes_data.decode("utf-8", errors="ignore")
