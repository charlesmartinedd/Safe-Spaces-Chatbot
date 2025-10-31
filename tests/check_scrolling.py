#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick check of scrolling behavior."""
import asyncio
import sys
import os
from pathlib import Path
from playwright.async_api import async_playwright

# Force UTF-8 output on Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


async def check_scrolling():
    """Check the scrolling behavior."""
    screenshots_dir = Path("tests/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible browser
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        try:
            print("🌐 Opening chatbot at http://localhost:5000")
            await page.goto("http://localhost:5000", wait_until="networkidle")
            await page.wait_for_selector("#chat-messages")

            print("✅ Page loaded")

            # Check CSS properties
            print("\n📊 Checking layout properties:")

            body_height = await page.evaluate("document.body.scrollHeight")
            body_overflow = await page.evaluate("window.getComputedStyle(document.body).overflow")
            viewport_height = await page.evaluate("window.innerHeight")

            print(f"  - Viewport height: {viewport_height}px")
            print(f"  - Body scrollHeight: {body_height}px")
            print(f"  - Body overflow: {body_overflow}")

            if body_height > viewport_height:
                print(f"  ⚠️ Body is taller than viewport ({body_height}px > {viewport_height}px)")
                print(f"  ⚠️ This will cause page scrolling!")
            else:
                print(f"  ✅ Body fits in viewport")

            # Check app-container
            app_container_height = await page.evaluate("""
                () => {
                    const el = document.querySelector('.app-container');
                    return {
                        scrollHeight: el.scrollHeight,
                        clientHeight: el.clientHeight,
                        height: window.getComputedStyle(el).height,
                        minHeight: window.getComputedStyle(el).minHeight,
                        overflow: window.getComputedStyle(el).overflow
                    };
                }
            """)
            print(f"\n  App Container:")
            print(f"    - height CSS: {app_container_height['height']}")
            print(f"    - min-height CSS: {app_container_height['minHeight']}")
            print(f"    - scrollHeight: {app_container_height['scrollHeight']}px")
            print(f"    - clientHeight: {app_container_height['clientHeight']}px")

            if app_container_height['scrollHeight'] > viewport_height:
                print(f"    ⚠️ Container is taller than viewport!")

            # Check chat-container
            chat_container = await page.evaluate("""
                () => {
                    const el = document.querySelector('.chat-container');
                    return {
                        scrollHeight: el.scrollHeight,
                        clientHeight: el.clientHeight,
                        overflow: window.getComputedStyle(el).overflow,
                        overflowY: window.getComputedStyle(el).overflowY
                    };
                }
            """)
            print(f"\n  Chat Container:")
            print(f"    - overflow: {chat_container['overflow']}")
            print(f"    - overflow-y: {chat_container['overflowY']}")
            print(f"    - scrollHeight: {chat_container['scrollHeight']}px")
            print(f"    - clientHeight: {chat_container['clientHeight']}px")

            # Check chat-messages
            chat_messages = await page.evaluate("""
                () => {
                    const el = document.querySelector('.chat-messages');
                    return {
                        scrollHeight: el.scrollHeight,
                        clientHeight: el.clientHeight,
                        overflow: window.getComputedStyle(el).overflow,
                        overflowY: window.getComputedStyle(el).overflowY
                    };
                }
            """)
            print(f"\n  Chat Messages:")
            print(f"    - overflow-y: {chat_messages['overflowY']}")
            print(f"    - scrollHeight: {chat_messages['scrollHeight']}px")
            print(f"    - clientHeight: {chat_messages['clientHeight']}px")

            if chat_messages['scrollHeight'] > chat_messages['clientHeight']:
                print(f"    ✅ Chat messages area is scrollable")
            else:
                print(f"    ℹ️ No overflow yet (content fits)")

            # Take screenshot
            await page.screenshot(path=str(screenshots_dir / "current_state.png"), full_page=True)
            print(f"\n📸 Screenshot saved: current_state.png")

            # Add several messages to test scrolling
            print("\n🧪 Adding multiple messages to test scrolling...")
            for i in range(5):
                await page.fill("#user-input", f"Test message {i+1}: I work with grade {i+1} students.")
                await page.click("#send-btn")
                await page.wait_for_timeout(1000)

            await page.wait_for_timeout(2000)

            # Check if page scrolled
            page_scroll = await page.evaluate("window.pageYOffset")
            print(f"\n📏 Page scroll position: {page_scroll}px")

            if page_scroll > 0:
                print(f"  ❌ Page has scrolled! This is the problem we need to fix.")
            else:
                print(f"  ✅ Page hasn't scrolled!")

            # Take final screenshot
            await page.screenshot(path=str(screenshots_dir / "with_messages.png"), full_page=True)
            print(f"📸 Screenshot saved: with_messages.png")

            print("\n⏸️ Browser will stay open for 30 seconds so you can interact...")
            print("   You can try scrolling to see the behavior yourself.")
            await page.wait_for_timeout(30000)

        except Exception as e:
            print(f"❌ Error: {e}")
            raise

        finally:
            await browser.close()


if __name__ == "__main__":
    print("="*60)
    print("Scrolling Behavior Check")
    print("="*60 + "\n")
    asyncio.run(check_scrolling())
