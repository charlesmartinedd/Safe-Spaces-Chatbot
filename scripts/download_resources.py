#!/usr/bin/env python3
"""
Download official Safe Spaces resources and normalize them into plain text files.
"""
import json
import logging
import re
from io import BytesIO
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "resources_official.json"
OUTPUT_DIR = BASE_DIR / "documents" / "official"

HEADERS = {
    "User-Agent": "SafeSpacesRAG/1.0 (+https://github.com/charlesmartinedd)"
}

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("download_resources")


def ensure_output_dir() -> None:
    """Create the output directory if needed."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_resources() -> Dict:
    """Load resource metadata from JSON."""
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def sanitize_text(text: str) -> str:
    """Collapse whitespace and strip leading/trailing spaces."""
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def extract_html_text(content: bytes, url: str) -> str:
    """Parse HTML content and extract readable text."""
    soup = BeautifulSoup(content, "html.parser")

    # Remove scripts, styles, navs that add noise.
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "form"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    return sanitize_text(text)


def extract_pdf_text(content: bytes) -> str:
    """Extract text from a PDF document."""
    buffer = BytesIO(content)
    reader = PdfReader(buffer)

    pages = []
    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
            pages.append(page_text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to extract a PDF page: %s", exc)

    combined = "\n\n".join(pages)
    return sanitize_text(combined)


def fetch_resource(resource: Dict) -> None:
    """Download and store a single resource."""
    url = resource["url"]
    output_name = resource["output"]
    title = resource["title"]

    logger.info("Fetching %s", url)
    try:
        response = requests.get(url, timeout=45, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Failed to fetch %s (%s)", url, exc)
        return

    content_type = response.headers.get("Content-Type", "").lower()
    parsed_url = urlparse(url)
    suffix = Path(parsed_url.path).suffix.lower()

    if "pdf" in content_type or suffix == ".pdf":
        text = extract_pdf_text(response.content)
        extension = ".pdf.txt"
    else:
        text = extract_html_text(response.content, url)
        extension = ".html.txt"

    if not text:
        logger.warning("No text extracted for %s", url)
        return

    output_file = OUTPUT_DIR / f"{output_name}{extension}"
    header = f"{title}\nSource: {url}\n\n"

    output_file.write_text(header + text, encoding="utf-8")
    logger.info("Saved %s (%d characters)", output_file, len(text))


def main() -> None:
    ensure_output_dir()
    resources = load_resources()
    for resource in resources:
        fetch_resource(resource)


if __name__ == "__main__":
    main()
