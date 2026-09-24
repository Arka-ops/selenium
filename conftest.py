"""
conftest.py
Shared pytest configuration and hooks.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "smoke: quick smoke test suite"
    )


def pytest_html_report_title(report):
    report.title = "Selenium Capstone – E-Commerce Automation Report"
