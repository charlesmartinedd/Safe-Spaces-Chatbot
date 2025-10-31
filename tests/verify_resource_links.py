"""
Verify all resource links in resources-web.json
Check for working links, ACEs Aware UCLA, and UCAAN Aces Aware LMS
"""
import json
import asyncio
import aiohttp
from pathlib import Path

async def check_url(session, url, resource_id, title):
    """Check if a URL is accessible"""
    try:
        async with session.head(url, allow_redirects=True, timeout=10) as response:
            status = response.status
            final_url = str(response.url)
            return {
                "id": resource_id,
                "title": title,
                "url": url,
                "status": status,
                "accessible": status < 400,
                "final_url": final_url if final_url != url else None
            }
    except asyncio.TimeoutError:
        return {
            "id": resource_id,
            "title": title,
            "url": url,
            "status": "TIMEOUT",
            "accessible": False,
            "error": "Request timed out"
        }
    except Exception as e:
        return {
            "id": resource_id,
            "title": title,
            "url": url,
            "status": "ERROR",
            "accessible": False,
            "error": str(e)
        }

async def verify_all_links():
    """Verify all resource links"""
    # Load resources
    resources_path = Path(__file__).parent.parent / "frontend" / "static" / "data" / "resources-web.json"
    with open(resources_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    resources = data['resources']

    # Search for UCLA and UCAAN links
    print("=" * 80)
    print("SEARCHING FOR SPECIFIC LINKS")
    print("=" * 80)

    ucla_links = []
    ucaan_links = []

    for resource in resources:
        url = resource['url'].lower()
        title = resource['title'].lower()

        if 'ucla' in url or 'ucla' in title:
            ucla_links.append({
                "id": resource['id'],
                "title": resource['title'],
                "url": resource['url']
            })

        if 'ucaan' in url or 'ucaan' in title or ('lms' in url and 'aces' in url):
            ucaan_links.append({
                "id": resource['id'],
                "title": resource['title'],
                "url": resource['url']
            })

    print(f"\n[SEARCH] UCLA Links Found: {len(ucla_links)}")
    for link in ucla_links:
        print(f"   [{link['id']}] {link['title']}")
        print(f"   URL: {link['url']}\n")

    print(f"[SEARCH] UCAAN/LMS Links Found: {len(ucaan_links)}")
    for link in ucaan_links:
        print(f"   [{link['id']}] {link['title']}")
        print(f"   URL: {link['url']}\n")

    if not ucla_links:
        print("[WARNING] NO ACEs Aware UCLA link found in resources!")

    if not ucaan_links:
        print("[WARNING] NO UCAAN Aces Aware LMS link found in resources!")

    # Verify all links
    print("\n" + "=" * 80)
    print("VERIFYING ALL RESOURCE LINKS")
    print("=" * 80)

    async with aiohttp.ClientSession() as session:
        tasks = [
            check_url(session, resource['url'], resource['id'], resource['title'])
            for resource in resources
        ]
        results = await asyncio.gather(*tasks)

    # Categorize results
    working = [r for r in results if r['accessible']]
    broken = [r for r in results if not r['accessible']]

    print(f"\n[OK] Working Links: {len(working)}/{len(resources)}")
    print(f"[ERROR] Broken Links: {len(broken)}/{len(resources)}")

    if broken:
        print("\n" + "=" * 80)
        print("BROKEN OR INACCESSIBLE LINKS")
        print("=" * 80)
        for result in broken:
            print(f"\n[BROKEN] [{result['id']}] {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Status: {result['status']}")
            if 'error' in result:
                print(f"   Error: {result['error']}")

    # Show redirects
    redirects = [r for r in results if r.get('final_url')]
    if redirects:
        print("\n" + "=" * 80)
        print("REDIRECTED LINKS")
        print("=" * 80)
        for result in redirects:
            print(f"\n[REDIRECT] [{result['id']}] {result['title']}")
            print(f"   Original: {result['url']}")
            print(f"   Redirects to: {result['final_url']}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Resources: {len(resources)}")
    print(f"Working Links: {len(working)} ({len(working)/len(resources)*100:.1f}%)")
    print(f"Broken Links: {len(broken)} ({len(broken)/len(resources)*100:.1f}%)")
    print(f"Redirected Links: {len(redirects)}")
    print(f"\nACEs Aware UCLA Links: {len(ucla_links)}")
    print(f"UCAAN Aces Aware LMS Links: {len(ucaan_links)}")

    return {
        "total": len(resources),
        "working": len(working),
        "broken": len(broken),
        "ucla_found": len(ucla_links) > 0,
        "ucaan_found": len(ucaan_links) > 0,
        "results": results
    }

if __name__ == "__main__":
    asyncio.run(verify_all_links())
