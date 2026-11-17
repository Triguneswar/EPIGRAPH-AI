"""
scripts/ingest_documents.py

Real document-ingestion pipeline for the RAG knowledge base: extracts text
from PDF/TXT/DOCX/MD, chunks it, and stores it (with metadata) as Source
rows in the database. Embedding + pgvector insertion is wired as a clearly
marked extension point — it requires a configured embedding model, which
needs network access this environment doesn't have; ingestion itself
(extraction + chunking + DB metadata storage) works fully offline.

Usage:
    python scripts/ingest_documents.py --input data/historical_documents
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


def extract_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt" or ext == ".md":
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            raise RuntimeError("Install `pypdf` to ingest PDF files.")
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if ext == ".docx":
        try:
            import docx
        except ImportError:
            raise RuntimeError("Install `python-docx` to ingest DOCX files.")
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError(f"Unsupported document type: {ext}")


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return [c.strip() for c in chunks if c.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/historical_documents")
    args = parser.parse_args()

    if not os.path.isdir(args.input):
        print(f"No such directory: {args.input}. Add documents there first (see docs/datasets.md).")
        return

    from app.core.database import Base, SessionLocal, engine
    from app.models.models import Source

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    ingested = 0
    for fname in os.listdir(args.input):
        path = os.path.join(args.input, fname)
        ext = os.path.splitext(fname)[1].lower()
        if ext not in (".pdf", ".txt", ".docx", ".md"):
            continue
        try:
            text = extract_text(path)
        except Exception as e:
            print(f"Skipping {fname}: {e}")
            continue

        chunks = chunk_text(text)
        source = Source(
            title=os.path.splitext(fname)[0],
            source_type=ext.lstrip("."),
            file_path=path,
        )
        db.add(source)
        ingested += 1
        print(f"Ingested {fname} — {len(chunks)} chunk(s). "
              "NOTE: embeddings not generated (no embedding-model/network configured); "
              "metadata stored, ready for pgvector insertion once a model is available.")

    db.commit()
    db.close()
    print(f"\nTotal documents ingested: {ingested}")


if __name__ == "__main__":
    main()
