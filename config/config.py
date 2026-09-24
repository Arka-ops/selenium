"""
config/config.py
Central configuration for the Selenium Capstone project.
Edit BASE_URL and credentials to switch to a different demo site.
"""

import os

# ── Application Under Test ────────────────────────────────────────────────────
BASE_URL      = "https://tutorialsninja.com/demo/"
VALID_EMAIL   = "arkopan84@gmail.com"   # pre-registered on the demo site
VALID_PASSWORD = "Arka@123"

# ── Browser ───────────────────────────────────────────────────────────────────
BROWSER       = "chrome"            # "chrome" | "firefox" | "edge"
HEADLESS      = False               # set True for CI environments

# ── Waits (seconds) ───────────────────────────────────────────────────────────
IMPLICIT_WAIT  = 15
EXPLICIT_WAIT  = 10

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREENSHOTS_DIR = os.path.join(ROOT_DIR, "screenshots")
REPORTS_DIR     = os.path.join(ROOT_DIR, "reports")
TEST_DATA_DIR   = os.path.join(ROOT_DIR, "test_data")
TEST_DATA_JSON  = os.path.join(TEST_DATA_DIR, "test_data.json")
TEST_DATA_EXCEL = os.path.join(TEST_DATA_DIR, "test_data.xlsx")

# ── Product to test ───────────────────────────────────────────────────────────
SEARCH_TERM    = "iPhone"
PRODUCT_QTY    = 2
