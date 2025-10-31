"""
Test resources page with screenshots in both languages
"""
import asyncio
from playwright.async_api import async_playwright

async def test_resources_page():
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

        # Take screenshot in English
        await page.screenshot(path='resources_english.png', full_page=True)
        print("English screenshot saved")

        # Click Spanish toggle
        await page.click('[data-lang="es"]')
        await page.wait_for_timeout(1000)  # Wait for re-render

        # Take screenshot in Spanish
        await page.screenshot(path='resources_spanish.png', full_page=True)
        print("Spanish screenshot saved")

        # Check card heights
        cards = await page.query_selector_all('.resource-card')
        print(f"\nFound {len(cards)} resource cards")

        for i, card in enumerate(cards[:5]):  # Check first 5 cards
            box = await card.bounding_box()
            print(f"Card {i+1}: width={box['width']:.1f}px, height={box['height']:.1f}px")

        # Check if page is scrollable
        scroll_height = await page.evaluate('document.documentElement.scrollHeight')
        client_height = await page.evaluate('document.documentElement.clientHeight')
        print(f"\nPage scroll height: {scroll_height}px")
        print(f"Page client height: {client_height}px")
        print(f"Scrollable: {scroll_height > client_height}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_resources_page())
