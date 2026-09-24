"""
utils/popup_handler.py

Handles:
    - JavaScript alerts
    - Cookie banners
    - Bootstrap/modal overlays

Important:
    close_modal() must NOT blindly click every button
    having class='close', because OpenCart success alerts
    can also contain close buttons.
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    NoAlertPresentException,
    NoSuchElementException,
    ElementClickInterceptedException
)


# ================================================================
# JAVASCRIPT ALERT
# ================================================================

def handle_alert(
    driver,
    timeout: int = 2
) -> str:

    try:

        alert = WebDriverWait(
            driver,
            timeout
        ).until(
            EC.alert_is_present()
        )

        text = alert.text

        print(
            f"  ⚠️  JavaScript alert found: {text}"
        )

        alert.accept()

        print(
            "  ✅  JavaScript alert accepted."
        )

        return text

    except (
        TimeoutException,
        NoAlertPresentException
    ):

        return ""


# ================================================================
# COOKIE BANNER
# ================================================================

def dismiss_cookie_banner(
    driver,
    timeout: int = 3
) -> bool:

    cookie_xpaths = [

        # Common cookie buttons
        "//button[contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'accept')]",

        "//button[contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'agree')]",

        "//a[contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'accept')]",

        # Common OneTrust
        "//*[@id='onetrust-accept-btn-handler']",

        # Generic cookie close
        "//*[contains(@id,'cookie')]"
        "//button[contains(@class,'close')]",
    ]

    for xpath in cookie_xpaths:

        try:

            element = WebDriverWait(
                driver,
                timeout
            ).until(
                EC.element_to_be_clickable(
                    (By.XPATH, xpath)
                )
            )

            driver.execute_script(
                "arguments[0].click();",
                element
            )

            print(
                "  🍪  Cookie banner dismissed."
            )

            time.sleep(0.3)

            return True

        except (
            TimeoutException,
            NoSuchElementException,
            ElementClickInterceptedException
        ):
            continue

    return False


# ================================================================
# MODAL
# ================================================================

def close_modal(
    driver,
    timeout: int = 3
) -> bool:
    """
    Close ONLY an actual visible modal.

    We intentionally DO NOT use:
        //button[contains(@class,'close')]

    because that can close the OpenCart success alert.
    """

    modal_xpaths = [

        # Bootstrap visible modal
        (
            "//div[contains(@class,'modal') "
            "and contains(@class,'show')]"
            "//button[contains(@class,'close')]"
        ),

        # Modal dismiss button
        (
            "//div[contains(@class,'modal') "
            "and contains(@class,'show')]"
            "//button[@data-dismiss='modal']"
        ),

        # Bootstrap 5
        (
            "//div[contains(@class,'modal') "
            "and contains(@class,'show')]"
            "//button[@data-bs-dismiss='modal']"
        ),
    ]

    for xpath in modal_xpaths:

        try:

            button = WebDriverWait(
                driver,
                timeout
            ).until(
                EC.element_to_be_clickable(
                    (By.XPATH, xpath)
                )
            )

            driver.execute_script(
                "arguments[0].click();",
                button
            )

            print(
                "  🪟  Modal closed."
            )

            time.sleep(0.3)

            return True

        except (
            TimeoutException,
            NoSuchElementException,
            ElementClickInterceptedException
        ):
            continue

    return False