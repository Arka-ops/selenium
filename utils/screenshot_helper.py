"""
utils/screenshot_helper.py
Saves timestamped screenshots and returns their paths.
"""

import os
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver

from config.config import SCREENSHOTS_DIR


def take_screenshot(driver: WebDriver, step_name: str) -> str:
    """
    Capture a screenshot and save it under screenshots/.
    Returns the absolute file path.
    """
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # sanitise step_name so it's safe as a filename
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in step_name)
    filename  = f"{safe_name}_{timestamp}.png"
    filepath  = os.path.join(SCREENSHOTS_DIR, filename)
    driver.save_screenshot(filepath)
    print(f"  📸  Screenshot saved → {filepath}")
    return filepath
