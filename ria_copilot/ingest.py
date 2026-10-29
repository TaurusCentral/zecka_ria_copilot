from __future__ import annotations
from pathlib import Path
from pypdf import PdfReader

def ingest_pdf(pdf_path: str, out_dir: str, source_url: str | None = None) -> list[str]:
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    reader=PdfReader(pdf_path); made=[]
    stem=Path(pdf_path).stem
    for i,page in enumerate(reader.pages,1):
        text=(page.extract_text() or "").strip()
        if not text: continue
        p=out/f"{stem}_p{i}.md"
        p.write_text(f"SOURCE: {source_url or Path(pdf_path).name}\nPAGE: {i}\n{text}\n",encoding="utf-8")
        made.append(str(p))
    return made
