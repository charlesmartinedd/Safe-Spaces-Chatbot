#!/usr/bin/env python3
"""
Extract references from the RRC References PDF.
"""

import os
import sys
from pathlib import Path
from pypdf import PdfReader
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_rrc_references(pdf_path: str, output_path: str) -> None:
    """Extract references from RRC References PDF."""

    pdf_path = Path(pdf_path)
    output_path = Path(output_path)

    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        sys.exit(1)

    logger.info(f"Opening PDF: {pdf_path}")

    try:
        reader = PdfReader(str(pdf_path))
        total_pages = len(reader.pages)
        logger.info(f"Total pages: {total_pages}")

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Extract all text
        all_text = []
        for page_num in range(total_pages):
            logger.info(f"Processing page {page_num + 1}/{total_pages}")
            try:
                page = reader.pages[page_num]
                text = page.extract_text()
                if text:
                    all_text.append(text)
            except Exception as e:
                logger.warning(f"Error extracting page {page_num + 1}: {e}")

        full_text = '\n\n'.join(all_text)

        # Write raw text
        logger.info(f"Writing extracted references to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)

        # Try to parse references
        logger.info("Attempting to parse references...")

        # Look for URLs
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', full_text)
        logger.info(f"Found {len(urls)} URLs")

        # Write structured output
        structured_output = output_path.parent / "rrc_references_structured.txt"
        with open(structured_output, 'w', encoding='utf-8') as f:
            f.write("# RRC References - Structured\n\n")
            f.write("## URLs Found:\n\n")
            for i, url in enumerate(set(urls), 1):
                f.write(f"{i}. {url}\n")
            f.write(f"\n\n## Full Text:\n\n")
            f.write(full_text)

        logger.info(f"✅ Extraction complete!")
        logger.info(f"Raw output: {output_path}")
        logger.info(f"Structured output: {structured_output}")

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Paths
    pdf_path = r"C:\Users\MarieLexisDad\Downloads\RRC References.pdf"
    output_path = r"C:\Users\MarieLexisDad\repos\Safe-Spaces-Chatbot\documents\rrc_references_extracted.txt"

    logger.info("Starting RRC References PDF extraction...")
    extract_rrc_references(pdf_path, output_path)
    logger.info("Done!")
