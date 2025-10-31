"""
Test the filtered resources page with screenshots
"""
import asyncio
from playwright.async_api import async_playwright

async def test_filtered_resources():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1400, 'height': 900})

        # Navigate to resources page
        url = "http://localhost:9111/resources.html"
        print(f"Navigating to {url}")
        await page.goto(url, wait_until='networkidle')

        # Wait for resources to load
        await page.wait_for_selector('.resource-card', timeout=10000)
        print("Resources loaded")

        # Count cards
        cards = await page.query_selector_all('.resource-card')
        print(f"\nTotal resources displayed: {len(cards)}")

        # Check result count text
        results_text = await page.text_content('#results-text')
        print(f"Results text: {results_text}")

        # Take screenshot in English
        await page.screenshot(path='resources_english_filtered.png', full_page=True)
        print("English screenshot saved")

        # Click Spanish toggle
        await page.click('[data-lang="es"]')
        await page.wait_for_timeout(1000)

        # Check Spanish result count
        results_text_es = await page.text_content('#results-text')
        print(f"Spanish results text: {results_text_es}")

        # Take screenshot in Spanish
        await page.screenshot(path='resources_spanish_filtered.png', full_page=True)
        print("Spanish screenshot saved")

        # Check a few cards for proper content
        print("\nSample Resource Cards:")
        print("=" * 80)
        for i, card in enumerate(cards[:3], start=1):
            title = await card.query_selector('.resource-title')
            title_text = await title.text_content() if title else "No title"
            print(f"Card {i}: {title_text}")

        # Check scrolling
        scroll_height = await page.evaluate('document.documentElement.scrollHeight')
        client_height = await page.evaluate('document.documentElement.clientHeight')
        print(f"\nScroll height: {scroll_height}px")
        print(f"Client height: {client_height}px")
        print(f"Scrollable: {scroll_height > client_height}")

        await browser.close()
        print("\n✓ Testing complete!")

if __name__ == "__main__":
    asyncio.run(test_filtered_resources())
