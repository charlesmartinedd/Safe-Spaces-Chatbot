#!/usr/bin/env python3
"""
Extract text from the large RRC Course PDF (28MB) efficiently.
Memory-safe processing with progress indicators.
"""

import os
import sys
from pathlib import Path
from pypdf import PdfReader
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_rrc_course(pdf_path: str, output_path: str) -> None:
    """Extract text from RRC Course PDF page by page."""

    pdf_path = Path(pdf_path)
    output_path = Path(output_path)

    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        sys.exit(1)

    logger.info(f"Opening PDF: {pdf_path}")
    logger.info(f"File size: {pdf_path.stat().st_size / (1024*1024):.2f} MB")

    try:
        reader = PdfReader(str(pdf_path))
        total_pages = len(reader.pages)
        logger.info(f"Total pages: {total_pages}")

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Extract text page by page
        extracted_text = []

        for page_num in range(total_pages):
            if page_num % 10 == 0:
                logger.info(f"Processing page {page_num + 1}/{total_pages} ({(page_num/total_pages)*100:.1f}%)")

            try:
                page = reader.pages[page_num]
                text = page.extract_text()

                if text and text.strip():
                    # Clean the text
                    text = text.strip()
                    # Add page marker
                    extracted_text.append(f"\n\n--- Page {page_num + 1} ---\n\n")
                    extracted_text.append(text)

            except Exception as e:
                logger.warning(f"Error extracting page {page_num + 1}: {e}")
                continue

        # Write to file
        logger.info(f"Writing extracted text to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(extracted_text))

        logger.info(f"✅ Extraction complete!")
        logger.info(f"Output file size: {output_path.stat().st_size / (1024*1024):.2f} MB")
        logger.info(f"Total characters: {len(''.join(extracted_text)):,}")

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Paths
    pdf_path = r"C:\Users\MarieLexisDad\Downloads\RRC Course.pdf"
    output_path = r"C:\Users\MarieLexisDad\repos\Safe-Spaces-Chatbot\documents\rrc_course_extracted.txt"

    logger.info("Starting RRC Course PDF extraction...")
    extract_rrc_course(pdf_path, output_path)
    logger.info("Done!")
