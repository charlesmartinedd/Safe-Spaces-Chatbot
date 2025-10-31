import os
import signal
import subprocess
import time
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON = Path(os.getenv("USERPROFILE")) / "AppData" / "Local" / "Programs" / "Python" / "Python312" / "python.exe"

server = None
try:
    env = os.environ.copy()
    env.setdefault("PYTHONPATH", str(REPO_ROOT))
    server = subprocess.Popen(
        [str(PYTHON), "-m", "uvicorn", "backend.main:app", "--port", "8000", "--log-level", "warning"],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    health_url = "http://127.0.0.1:8000/api/health"
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            requests.get(health_url, timeout=1)
            break
        except requests.RequestException:
            time.sleep(0.5)
    else:
        raise RuntimeError(f"Server did not start in time when polling {health_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:8000", wait_until="networkidle")
        assert "RRC" in page.title(), "Page title missing"
        header_text = page.locator(".branding h1").inner_text()
        assert "RRC" in header_text
        scenario_count = page.locator(".scenario-btn").count()
        assert scenario_count >= 4, "Expected scenario buttons"
        screenshot_path = REPO_ROOT / "frontend" / "static" / "images"
        screenshot_path.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot_path / "headless-preview.png"), full_page=True)
        browser.close()
finally:
    if server and server.poll() is None:
        if os.name == "nt":
            server.send_signal(signal.CTRL_BREAK_EVENT)
            time.sleep(1)
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()

    script_path = Path(__file__)
    if script_path.exists():
        script_path.unlink()
