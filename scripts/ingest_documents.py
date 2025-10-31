#!/usr/bin/env python3
"""
Ingest downloaded resources into the ChromaDB collection used by the chatbot.
"""
import argparse
import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from backend.services.rag_service import RAGService

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("ingest_documents")

DEFAULT_DIRECTORIES = [
    Path("documents/official"),
    Path("documents"),
]


def iter_documents(paths):
    """Yield text content and filenames from provided directories."""
    seen = set()
    for base in paths:
        if not base.exists():
            continue
        for file_path in sorted(base.glob("*.txt")):
            resolved = file_path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            yield file_path.name, file_path.read_text(encoding="utf-8")


def main(clear: bool) -> None:
    rag = RAGService()
    if clear:
        logger.info("Clearing existing collection before ingestion.")
        rag.clear_collection()

    total_chunks = 0
    for filename, text in iter_documents(DEFAULT_DIRECTORIES):
        if not text.strip():
            logger.warning("Skipping %s (no text)", filename)
            continue
        chunks = rag.add_document(text, filename)
        total_chunks += chunks
        logger.info("Ingested %s (%d chunks)", filename, chunks)

    logger.info("Ingestion complete. Total chunks: %d", total_chunks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest text documents into the RAG collection.")
    parser.add_argument("--clear", action="store_true", help="Clear the existing collection before ingestion.")
    args = parser.parse_args()
    main(clear=args.clear)
