#!/usr/bin/env python3
"""
Ingest RRC Course and References into ChromaDB.
This script loads the extracted RRC content into the RAG database.
"""
import os
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.rag_service import RAGService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('. ')
            if last_period > chunk_size // 2:
                end = start + last_period + 2
                chunk = text[start:end]

        chunks.append(chunk.strip())
        start = end - overlap

    return chunks


def ingest_rrc_course():
    """Ingest RRC Course content into ChromaDB."""
    logger.info("="*60)
    logger.info("Ingesting RRC Course Content")
    logger.info("="*60)

    course_path = Path("documents/rrc_course_extracted.txt")
    if not course_path.exists():
        logger.error(f"RRC Course file not found: {course_path}")
        return False

    logger.info(f"Reading: {course_path}")
    with open(course_path, 'r', encoding='utf-8') as f:
        course_text = f.read()

    logger.info(f"Course content: {len(course_text):,} characters")

    # Split into chunks
    logger.info("Splitting into chunks...")
    chunks = chunk_text(course_text, chunk_size=800, overlap=150)
    logger.info(f"Created {len(chunks)} chunks")

    # Initialize RAG service
    logger.info("Initializing RAG service...")
    rag_service = RAGService()

    # Add course as a single document (RAGService will chunk it)
    logger.info("Adding RRC Course to database...")
    try:
        chunks_added = rag_service.add_document(course_text, "RRC Course")
        logger.info(f"✅ Successfully added RRC Course ({chunks_added} chunks)")
        success_count = chunks_added
    except Exception as e:
        logger.error(f"Error adding RRC Course: {e}")
        success_count = 0

    logger.info(f"✅ RRC Course ingestion: {success_count} chunks added")
    return True


def ingest_rrc_references():
    """Ingest RRC References into ChromaDB."""
    logger.info("="*60)
    logger.info("Ingesting RRC References")
    logger.info("="*60)

    refs_path = Path("documents/rrc_references_extracted.txt")
    if not refs_path.exists():
        logger.error(f"RRC References file not found: {refs_path}")
        return False

    logger.info(f"Reading: {refs_path}")
    with open(refs_path, 'r', encoding='utf-8') as f:
        refs_text = f.read()

    logger.info(f"References content: {len(refs_text):,} characters")

    # Split by reference (assuming each URL is on a new line)
    lines = refs_text.strip().split('\n')
    references = [line.strip() for line in lines if line.strip() and ('http' in line or len(line) > 30)]

    logger.info(f"Found {len(references)} references")

    # Initialize RAG service
    logger.info("Initializing RAG service...")
    rag_service = RAGService()

    # Add references to database
    logger.info("Adding references to database...")
    success_count = 0

    for i, ref in enumerate(references):
        try:
            # Extract source name if possible
            source_name = f"RRC_Reference_{i+1}"
            if "http" in ref:
                # Try to extract domain or meaningful name
                parts = ref.split('//')
                if len(parts) > 1:
                    domain = parts[1].split('/')[0]
                    source_name = f"RRC_Ref_{i+1}_{domain}"

            # Add each reference as a document
            chunks_added = rag_service.add_document(ref, source_name)
            success_count += chunks_added

            if (i+1) % 10 == 0:
                logger.info(f"Processed {i+1}/{len(references)} references")

        except Exception as e:
            logger.error(f"Error adding reference {i+1}: {e}")

    logger.info(f"✅ RRC References ingestion: {success_count} chunks added from {len(references)} references")
    return True


def main():
    """Main ingestion workflow."""
    logger.info("\n" + "="*60)
    logger.info("RRC Content Ingestion Script")
    logger.info("="*60 + "\n")

    # Check if files exist
    course_path = Path("documents/rrc_course_extracted.txt")
    refs_path = Path("documents/rrc_references_extracted.txt")

    if not course_path.exists():
        logger.error(f"❌ RRC Course file not found: {course_path}")
        logger.info("Please run: python scripts/extract_rrc_course.py")
        return False

    if not refs_path.exists():
        logger.error(f"❌ RRC References file not found: {refs_path}")
        logger.info("Please run: python scripts/extract_rrc_references.py")
        return False

    # Ingest course content
    course_success = ingest_rrc_course()

    # Ingest references
    refs_success = ingest_rrc_references()

    # Summary
    logger.info("\n" + "="*60)
    logger.info("Ingestion Complete")
    logger.info("="*60)
    logger.info(f"RRC Course: {'✅ Success' if course_success else '❌ Failed'}")
    logger.info(f"RRC References: {'✅ Success' if refs_success else '❌ Failed'}")

    if course_success and refs_success:
        logger.info("\n✅ All RRC content successfully ingested into ChromaDB!")
        logger.info("The chatbot is now ready to use with RRC course knowledge.")
        return True
    else:
        logger.error("\n❌ Some content failed to ingest. Check logs above.")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
