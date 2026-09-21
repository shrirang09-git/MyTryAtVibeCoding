"""Visit the Streamlit app in a real headless browser so it counts as genuine use.

A plain HTTP request only fetches the static HTML shell; Streamlit Community
Cloud only treats the app as "in use" when a browser renders it and holds a
live session. If the app has already gone to sleep, this also clicks the
"get this app back up" button. Exits non-zero if the app never comes up, so
a broken keep-alive shows as a failed run instead of silently "succeeding".
"""

import re
import sys
import time

from playwright.sync_api import sync_playwright

URL = "https://po-twin.streamlit.app/"
WAKE_BUTTON = re.compile(r"back up", re.IGNORECASE)
APP_MARKER = '[data-testid="stApp"]'
GIVE_UP_AFTER_S = 240
STAY_CONNECTED_S = 45


def first_match(page, selector, **kwargs):
    """Look for an element in the page and in every iframe (the app and the
    sleep screen are both rendered inside iframes on Community Cloud)."""
    for frame in page.frames:
        locator = frame.locator(selector, **kwargs)
        if locator.count():
            return locator.first
    return None


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=60_000)

        deadline = time.time() + GIVE_UP_AFTER_S
        clicked_wake = False
        while time.time() < deadline:
            wake = first_match(page, "button", has_text=WAKE_BUTTON)
            if wake and not clicked_wake:
                wake.click()
                clicked_wake = True
                print("App was asleep - clicked the wake-up button.")

            if first_match(page, APP_MARKER):
                print("App is up" + (" (after waking it)." if clicked_wake else "."))
                page.wait_for_timeout(STAY_CONNECTED_S * 1000)
                browser.close()
                return 0

            page.wait_for_timeout(2000)

        print(f"App did not come up within {GIVE_UP_AFTER_S}s.", file=sys.stderr)
        browser.close()
        return 1


if __name__ == "__main__":
    sys.exit(main())
