"""
Filter resources to keep only verified working links
"""
import json
from pathlib import Path

# IDs of working resources from verification
WORKING_IDS = [3, 8, 9, 12, 16, 20, 27, 28, 29, 31, 32, 33, 36, 38, 40]

def filter_resources():
    # Load current resources
    resources_path = Path(__file__).parent.parent / "frontend" / "static" / "data" / "resources-web.json"
    with open(resources_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Filter to working resources only
    working_resources = [r for r in data['resources'] if r['id'] in WORKING_IDS]

    # Re-number from 1 to 15
    for i, resource in enumerate(working_resources, start=1):
        resource['id'] = i

    print(f"Original resources: {len(data['resources'])}")
    print(f"Working resources: {len(working_resources)}")
    print(f"Removed: {len(data['resources']) - len(working_resources)}")

    # Create updated data
    updated_data = {
        "resources": working_resources
    }

    # Write back to file
    with open(resources_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)

    print(f"\nUpdated resources-web.json with {len(working_resources)} verified resources")

    # Show the resources
    print("\nVerified Working Resources:")
    print("=" * 80)
    for resource in working_resources:
        print(f"[{resource['id']}] {resource['title']}")
        print(f"    URL: {resource['url']}")
        print(f"    Category: {resource['category']}")
        print()

if __name__ == "__main__":
    filter_resources()
