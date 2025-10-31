#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright UI test for RRC Support Coach chatbot.
Takes screenshots for design validation.
"""
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


async def test_chatbot_ui():
    """Test the chatbot UI and take screenshots."""

    screenshots_dir = Path("tests/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        # Launch browser in headless mode
        browser = await p.chromium.launch(headless=True)

        # Create new page with desktop viewport
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        try:
            print("📸 Opening chatbot...")
            await page.goto("http://localhost:5000", wait_until="networkidle")

            # Wait for page to fully load
            await page.wait_for_selector(".header-logo img")
            await page.wait_for_selector(".gradient-line")
            await page.wait_for_selector("#chat-messages")

            print("✅ Page loaded successfully")

            # Take initial screenshot
            await page.screenshot(path=str(screenshots_dir / "01_initial_load.png"), full_page=True)
            print("📸 Screenshot saved: 01_initial_load.png")

            # Check header elements
            header = await page.query_selector(".header")
            if header:
                print("✅ Header found")

            logo = await page.query_selector(".header-logo img")
            if logo:
                logo_src = await logo.get_attribute("src")
                print(f"✅ Logo found: {logo_src}")

            gradient_line = await page.query_selector(".gradient-line")
            if gradient_line:
                print("✅ Gradient line found")

            # Check welcome message
            welcome_msg = await page.query_selector(".bot-message .message-text")
            if welcome_msg:
                welcome_text = await welcome_msg.inner_text()
                word_count = len(welcome_text.split())
                print(f"✅ Welcome message found ({word_count} words)")
                if word_count > 50:
                    print(f"⚠️ Warning: Welcome message is {word_count} words (should be ~35)")

            # Take screenshot of chat area
            chat_container = await page.query_selector(".chat-container")
            if chat_container:
                await chat_container.screenshot(path=str(screenshots_dir / "02_chat_area.png"))
                print("📸 Screenshot saved: 02_chat_area.png")

            # Test user input
            print("\n🧪 Testing user interaction...")
            user_input = await page.query_selector("#user-input")
            if user_input:
                await user_input.fill("I work with 3rd grade students and I'm a classroom teacher. How can I help a student who seems withdrawn?")
                print("✅ Filled user input")

                # Take screenshot with input
                await page.screenshot(path=str(screenshots_dir / "03_user_input.png"), full_page=True)
                print("📸 Screenshot saved: 03_user_input.png")

                # Click send button
                send_btn = await page.query_selector("#send-btn")
                if send_btn:
                    await send_btn.click()
                    print("✅ Clicked send button")

                    # Wait for response
                    print("⏳ Waiting for AI response...")
                    await page.wait_for_timeout(5000)  # Wait 5 seconds for response

                    # Take screenshot after response
                    await page.screenshot(path=str(screenshots_dir / "04_with_response.png"), full_page=True)
                    print("📸 Screenshot saved: 04_with_response.png")

                    # Check if response contains HTML formatting
                    bot_messages = await page.query_selector_all(".bot-message .message-text")
                    if len(bot_messages) > 1:
                        last_msg = bot_messages[-1]
                        html_content = await last_msg.inner_html()

                        # Check for HTML tags
                        has_strong = "<strong>" in html_content
                        has_ul = "<ul>" in html_content
                        has_li = "<li>" in html_content
                        has_p = "<p>" in html_content

                        print(f"\n📋 Response formatting check:")
                        print(f"  - <strong> tags: {'✅' if has_strong else '❌'}")
                        print(f"  - <ul> tags: {'✅' if has_ul else '❌'}")
                        print(f"  - <li> tags: {'✅' if has_li else '❌'}")
                        print(f"  - <p> tags: {'✅' if has_p else '❌'}")

                        # Check for markdown (should NOT exist)
                        has_markdown_bold = "**" in html_content
                        has_markdown_header = "##" in html_content

                        if has_markdown_bold or has_markdown_header:
                            print(f"  ⚠️ Warning: Markdown detected (should be HTML only)")

            # Test mobile viewport
            print("\n📱 Testing mobile viewport...")
            await page.set_viewport_size({"width": 375, "height": 667})
            await page.wait_for_timeout(1000)
            await page.screenshot(path=str(screenshots_dir / "05_mobile_view.png"), full_page=True)
            print("📸 Screenshot saved: 05_mobile_view.png")

            # Check CSS properties
            print("\n🎨 Checking design elements...")

            # Check body overflow (should be hidden for no page scroll)
            body_overflow = await page.evaluate("window.getComputedStyle(document.body).overflow")
            print(f"  - Body overflow: {body_overflow} {'✅' if body_overflow == 'hidden' else '❌ (should be hidden)'}")

            # Check bot message background color
            bot_msg_bg = await page.evaluate("""
                () => {
                    const el = document.querySelector('.bot-message .message-content');
                    return el ? window.getComputedStyle(el).backgroundColor : null;
                }
            """)
            print(f"  - Bot message bg: {bot_msg_bg}")

            # Check border width
            bot_msg_border = await page.evaluate("""
                () => {
                    const el = document.querySelector('.bot-message .message-content');
                    return el ? window.getComputedStyle(el).borderWidth : null;
                }
            """)
            print(f"  - Border width: {bot_msg_border} {'✅' if '2px' in str(bot_msg_border) else '❌ (should be 2px)'}")

            print("\n✅ All tests completed successfully!")
            print(f"📁 Screenshots saved to: {screenshots_dir.absolute()}")

        except Exception as e:
            print(f"❌ Error during testing: {e}")
            await page.screenshot(path=str(screenshots_dir / "error.png"))
            raise

        finally:
            await browser.close()


if __name__ == "__main__":
    print("=" * 60)
    print("RRC Support Coach UI Test Suite")
    print("=" * 60)
    print()

    try:
        asyncio.run(test_chatbot_ui())
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)
