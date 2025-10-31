#!/usr/bin/env python3
"""
Export resources from RAG database to structured JSON.
Creates a resources.json file for the modal interface.
"""
import sys
import json
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.rag_service import RAGService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_resources():
    """Extract all resources from ChromaDB and structure them."""
    logger.info("Initializing RAG service...")
    rag_service = RAGService()

    # Get all documents from the collection
    logger.info("Fetching all documents from ChromaDB...")
    collection_data = rag_service.collection.get()

    documents = collection_data.get('documents', [])
    metadatas = collection_data.get('metadatas', [])
    ids = collection_data.get('ids', [])

    logger.info(f"Found {len(documents)} document chunks")

    # Group by source
    resources_by_source = {}

    for i, (doc, meta, doc_id) in enumerate(zip(documents, metadatas, ids)):
        source = meta.get('source', 'Unknown')
        chunk_num = meta.get('chunk', 0)

        if source not in resources_by_source:
            resources_by_source[source] = {
                'chunks': [],
                'full_text': []
            }

        resources_by_source[source]['chunks'].append({
            'id': doc_id,
            'chunk': chunk_num,
            'text': doc
        })
        resources_by_source[source]['full_text'].append(doc)

    logger.info(f"Grouped into {len(resources_by_source)} unique sources")

    # Structure as resources
    resources = []
    resource_id = 1

    for source_name, data in resources_by_source.items():
        # Combine chunks to get full content
        full_content = '\n\n'.join(data['full_text'])

        # Extract first 200 chars for description
        description = full_content[:200].strip()
        if len(full_content) > 200:
            description += "..."

        # Determine category
        category = categorize_resource(source_name, full_content)

        # Determine if it's a URL
        url = None
        if source_name.startswith('RRC_Ref_'):
            # Extract URL from content if present
            lines = full_content.split('\n')
            for line in lines:
                if line.startswith('http'):
                    url = line.strip()
                    break

        # Create resource entry
        resource = {
            'id': resource_id,
            'title': format_title(source_name),
            'description': description,
            'category': category,
            'source': source_name,
            'url': url,
            'chunkCount': len(data['chunks']),
            'fullContent': full_content,
            'gradeLevels': ['K-12'],  # Default for all RRC content
            'keywords': extract_keywords(full_content)
        }

        resources.append(resource)
        resource_id += 1

    # Sort by category, then title
    resources.sort(key=lambda x: (x['category'], x['title']))

    logger.info(f"Created {len(resources)} structured resources")

    # Save to JSON
    output_path = Path('frontend/static/data/resources.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({'resources': resources}, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Resources saved to: {output_path}")

    # Print summary
    print("\n" + "="*60)
    print("Resources Export Summary")
    print("="*60)

    categories = {}
    for resource in resources:
        cat = resource['category']
        categories[cat] = categories.get(cat, 0) + 1

    print(f"\nTotal Resources: {len(resources)}")
    print("\nBy Category:")
    for cat, count in sorted(categories.items()):
        print(f"  - {cat}: {count}")

    print(f"\nWith URLs: {sum(1 for r in resources if r['url'])}")
    print(f"Course Content: {sum(1 for r in resources if 'Course' in r['source'])}")

    return resources


def categorize_resource(source_name, content):
    """Determine resource category based on source and content."""
    source_lower = source_name.lower()
    content_lower = content.lower()

    if 'course' in source_lower:
        return 'RRC Course Materials'
    elif 'ref' in source_lower or 'reference' in source_lower:
        if 'apa.org' in content_lower or 'research' in content_lower:
            return 'Research & Evidence'
        elif 'ca.gov' in content_lower or 'california' in content_lower:
            return 'California Guidelines'
        else:
            return 'External Resources'
    elif 'guideline' in content_lower or 'policy' in content_lower:
        return 'California Guidelines'
    elif 'strategy' in content_lower or 'classroom' in content_lower:
        return 'Classroom Strategies'
    else:
        return 'RRC Course Materials'


def format_title(source_name):
    """Format source name into a readable title."""
    # Remove technical prefixes
    title = source_name.replace('RRC_Ref_', 'Reference ')
    title = title.replace('RRC_Reference_', 'Reference ')
    title = title.replace('_', ' ')

    # Clean up
    if title.startswith('RRC Course'):
        return 'RRC Course Content'

    return title.strip()


def extract_keywords(content):
    """Extract key terms from content for search."""
    content_lower = content.lower()
    keywords = []

    # Common important terms
    key_terms = [
        'trauma', 'aces', 'toxic stress', 'resilience',
        'relationship', 'connection', 'safety', 'regulation',
        'classroom', 'student', 'teacher', 'support',
        'mental health', 'wellness', 'behavior', 'emotion'
    ]

    for term in key_terms:
        if term in content_lower:
            keywords.append(term)

    return keywords[:10]  # Limit to 10 keywords


if __name__ == "__main__":
    try:
        resources = extract_resources()
        logger.info("✅ Export complete!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Export failed: {e}", exc_info=True)
        sys.exit(1)
