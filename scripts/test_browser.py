#!/usr/bin/env python3
"""
Playwright headless browser testing script for Safe Spaces Chatbot
Tests UI, functionality, and performance with dev tools integration
"""
import asyncio
import sys
from playwright.async_api import async_playwright
import json
import time

async def test_chatbot():
    """Run comprehensive browser tests"""
    results = {
        "ui_tests": [],
        "api_tests": [],
        "performance": {},
        "console_logs": [],
        "network_requests": [],
        "errors": []
    }

    async with async_playwright() as p:
        # Launch browser with dev tools enabled
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-dev-shm-usage', '--no-sandbox']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            record_video_dir='./test_videos' if False else None  # Set to True to record
        )

        page = await context.new_page()

        # Enable console logging
        page.on("console", lambda msg: results["console_logs"].append({
            "type": msg.type,
            "text": msg.text,
            "location": msg.location
        }))

        # Enable network monitoring
        page.on("request", lambda request: results["network_requests"].append({
            "url": request.url,
            "method": request.method,
            "timestamp": time.time()
        }))

        # Track errors
        page.on("pageerror", lambda exc: results["errors"].append(str(exc)))

        try:
            print("\n" + "="*60)
            print("🧪 SAFE SPACES CHATBOT - BROWSER TESTING")
            print("="*60)

            # Test 1: Page Load
            print("\n[1/7] Testing page load...")
            start_time = time.time()
            response = await page.goto('http://localhost:5000', wait_until='networkidle', timeout=30000)
            load_time = time.time() - start_time
            results["performance"]["page_load_time"] = load_time

            if response.status == 200:
                results["ui_tests"].append({"test": "Page Load", "status": "PASS", "time": f"{load_time:.2f}s"})
                print(f"   ✓ Page loaded successfully ({load_time:.2f}s)")
            else:
                results["ui_tests"].append({"test": "Page Load", "status": "FAIL", "error": f"Status {response.status}"})
                print(f"   ✗ Page load failed with status {response.status}")
                return results

            # Test 2: UI Elements Present
            print("\n[2/7] Checking UI elements...")
            ui_checks = {
                "Chat container": "#chat-container",
                "Chat messages area": "#chat-messages",
                "User input": "#user-input",
                "Send button": "#send-btn",
                "Upload section": ".upload-section",
                "RAG toggle": "#rag-toggle"
            }

            for name, selector in ui_checks.items():
                try:
                    element = await page.wait_for_selector(selector, timeout=5000)
                    is_visible = await element.is_visible()
                    if is_visible:
                        results["ui_tests"].append({"test": f"UI: {name}", "status": "PASS"})
                        print(f"   ✓ {name} found and visible")
                    else:
                        results["ui_tests"].append({"test": f"UI: {name}", "status": "WARN", "note": "Not visible"})
                        print(f"   ⚠ {name} found but not visible")
                except Exception as e:
                    results["ui_tests"].append({"test": f"UI: {name}", "status": "FAIL", "error": str(e)})
                    print(f"   ✗ {name} not found: {str(e)}")

            # Test 3: Health Check API
            print("\n[3/7] Testing health check API...")
            try:
                api_response = await page.evaluate("""
                    async () => {
                        const response = await fetch('/api/health');
                        return {
                            status: response.status,
                            data: await response.json()
                        };
                    }
                """)

                if api_response['status'] == 200:
                    data = api_response['data']
                    results["api_tests"].append({
                        "endpoint": "/api/health",
                        "status": "PASS",
                        "data": data
                    })
                    print(f"   ✓ Health check passed")
                    print(f"      - Status: {data.get('status')}")
                    print(f"      - Default Provider: {data.get('default_provider')}")
                    print(f"      - Available Providers: {data.get('providers')}")
                    print(f"      - Documents: {data.get('documents_count')}")
                else:
                    results["api_tests"].append({
                        "endpoint": "/api/health",
                        "status": "FAIL",
                        "error": f"Status {api_response['status']}"
                    })
                    print(f"   ✗ Health check failed: {api_response['status']}")
            except Exception as e:
                results["errors"].append(f"Health check error: {str(e)}")
                print(f"   ✗ Health check error: {str(e)}")

            # Test 4: Send Chat Message
            print("\n[4/7] Testing chat functionality with Grok API...")
            try:
                # Type message
                await page.fill("#user-input", "Hello! Can you help me?")
                await page.click("#send-btn")

                # Wait for response (increased timeout for API call)
                await page.wait_for_selector(".message.bot", timeout=30000)

                # Check if bot response appears
                bot_messages = await page.query_selector_all(".message.bot")
                if len(bot_messages) > 0:
                    bot_text = await bot_messages[-1].inner_text()
                    results["ui_tests"].append({
                        "test": "Chat Message - Grok Response",
                        "status": "PASS",
                        "response_preview": bot_text[:100]
                    })
                    print(f"   ✓ Bot responded: {bot_text[:80]}...")
                else:
                    results["ui_tests"].append({
                        "test": "Chat Message - Grok Response",
                        "status": "FAIL",
                        "error": "No bot response"
                    })
                    print(f"   ✗ No bot response received")
            except Exception as e:
                results["errors"].append(f"Chat test error: {str(e)}")
                print(f"   ✗ Chat test failed: {str(e)}")

            # Test 5: RAG Toggle
            print("\n[5/7] Testing RAG toggle...")
            try:
                rag_toggle = await page.query_selector("#rag-toggle")
                is_checked = await rag_toggle.is_checked()
                print(f"   ✓ RAG toggle found (currently: {'ON' if is_checked else 'OFF'})")

                # Toggle it
                await rag_toggle.click()
                await asyncio.sleep(0.5)
                new_state = await rag_toggle.is_checked()

                if new_state != is_checked:
                    results["ui_tests"].append({
                        "test": "RAG Toggle",
                        "status": "PASS",
                        "note": f"Toggled from {is_checked} to {new_state}"
                    })
                    print(f"   ✓ RAG toggle works (changed to: {'ON' if new_state else 'OFF'})")
                else:
                    results["ui_tests"].append({
                        "test": "RAG Toggle",
                        "status": "WARN",
                        "note": "State didn't change"
                    })
                    print(f"   ⚠ RAG toggle clicked but state unchanged")
            except Exception as e:
                results["errors"].append(f"RAG toggle test error: {str(e)}")
                print(f"   ✗ RAG toggle test failed: {str(e)}")

            # Test 6: Performance Metrics
            print("\n[6/7] Collecting performance metrics...")
            try:
                performance = await page.evaluate("""
                    () => {
                        const perf = window.performance;
                        const timing = perf.timing;
                        return {
                            dom_content_loaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                            page_load_complete: timing.loadEventEnd - timing.navigationStart,
                            dom_interactive: timing.domInteractive - timing.navigationStart,
                            memory: performance.memory ? {
                                used: performance.memory.usedJSHeapSize,
                                total: performance.memory.totalJSHeapSize,
                                limit: performance.memory.jsHeapSizeLimit
                            } : null
                        };
                    }
                """)

                results["performance"].update(performance)
                print(f"   ✓ DOM Content Loaded: {performance['dom_content_loaded']}ms")
                print(f"   ✓ Page Load Complete: {performance['page_load_complete']}ms")
                print(f"   ✓ DOM Interactive: {performance['dom_interactive']}ms")

                if performance['memory']:
                    mem_used_mb = performance['memory']['used'] / 1024 / 1024
                    print(f"   ✓ Memory Used: {mem_used_mb:.2f} MB")
            except Exception as e:
                print(f"   ⚠ Performance metrics partially available: {str(e)}")

            # Test 7: Screenshot
            print("\n[7/7] Taking screenshot...")
            await page.screenshot(path='./test_screenshot.png')
            print(f"   ✓ Screenshot saved: test_screenshot.png")

            # Summary
            print("\n" + "="*60)
            print("📊 TEST SUMMARY")
            print("="*60)

            passed = sum(1 for t in results["ui_tests"] + results["api_tests"] if t.get("status") == "PASS")
            failed = sum(1 for t in results["ui_tests"] + results["api_tests"] if t.get("status") == "FAIL")
            warnings = sum(1 for t in results["ui_tests"] + results["api_tests"] if t.get("status") == "WARN")

            print(f"\nTests: {passed} passed, {failed} failed, {warnings} warnings")
            print(f"Console Logs: {len(results['console_logs'])}")
            print(f"Network Requests: {len(results['network_requests'])}")
            print(f"Errors: {len(results['errors'])}")

            if results['errors']:
                print("\n⚠️  Errors encountered:")
                for err in results['errors'][:5]:  # Show first 5 errors
                    print(f"   - {err}")

            # Save detailed results
            with open('test_results.json', 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n✓ Detailed results saved: test_results.json")

        except Exception as e:
            print(f"\n❌ Critical test failure: {str(e)}")
            results["errors"].append(f"Critical: {str(e)}")

        finally:
            await browser.close()

    return results

if __name__ == "__main__":
    print("Starting browser tests...")
    try:
        results = asyncio.run(test_chatbot())

        # Exit with appropriate code
        if results.get("errors") or any(t.get("status") == "FAIL" for t in results.get("ui_tests", []) + results.get("api_tests", [])):
            sys.exit(1)
        else:
            print("\n✅ All critical tests passed!")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        sys.exit(1)
