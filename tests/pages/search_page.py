"""
tests/pages/search_page.py

Page Object for Search Results
Tutorials Ninja / OpenCart Demo
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)

from .base_page import BasePage
from config.config import EXPLICIT_WAIT, BASE_URL


class SearchPage(BasePage):

    # ================================================================
    # SEARCH
    # ================================================================

    SEARCH_INPUT = (
        By.NAME,
        "search"
    )

    SEARCH_BUTTON = (
        By.CSS_SELECTOR,
        "#search button"
    )

    SEARCH_RESULTS = (
        By.CSS_SELECTOR,
        ".product-layout"
    )

    # More general fallback
    SEARCH_RESULTS_FALLBACK = (
        By.XPATH,
        "//div[contains(@class,'product-layout')]"
    )

    # ================================================================
    # PRODUCT
    # ================================================================

    PRODUCT_NAME = (
        By.CSS_SELECTOR,
        "h4 a"
    )

    ADD_TO_CART_BUTTON = (
        By.XPATH,
        ".//button[contains(@onclick,'cart.add')]"
    )

    ADD_TO_CART_BUTTON_FALLBACK = (
        By.XPATH,
        ".//button[contains(@data-original-title,'Add to Cart')]"
    )

    # ================================================================
    # SUCCESS / CART
    # ================================================================

    SUCCESS_ALERT = (
        By.XPATH,
        "//div[contains(@class,'alert-success')]"
    )

    CART_TOTAL = (
        By.ID,
        "cart-total"
    )

    CART_BUTTON = (
        By.XPATH,
        "//span[@id='cart-total']/ancestor::button"
    )

    # ================================================================
    # SEARCH
    # ================================================================

    def search(self, search_term: str):

        print(
            f"\n  🔎  Searching for: {search_term}"
        )

        search_box = WebDriverWait(
            self.driver,
            EXPLICIT_WAIT
        ).until(
            EC.visibility_of_element_located(
                self.SEARCH_INPUT
            )
        )

        search_box.clear()
        search_box.send_keys(search_term)

        try:

            search_button = WebDriverWait(
                self.driver,
                EXPLICIT_WAIT
            ).until(
                EC.element_to_be_clickable(
                    self.SEARCH_BUTTON
                )
            )

            search_button.click()

        except TimeoutException:

            # Press ENTER if button cannot be clicked.
            from selenium.webdriver.common.keys import Keys

            search_box.send_keys(Keys.ENTER)

        # Wait for results
        try:

            WebDriverWait(
                self.driver,
                EXPLICIT_WAIT
            ).until(
                lambda d:
                len(self.get_product_elements()) > 0
            )

        except TimeoutException:
            pass

        time.sleep(0.5)

        print(
            f"  🔎  Products found: "
            f"{self.get_product_count()}"
        )

    # ================================================================
    # RESULTS
    # ================================================================

    def get_product_elements(self):

        products = self.driver.find_elements(
            *self.SEARCH_RESULTS
        )

        if products:
            return products

        return self.driver.find_elements(
            *self.SEARCH_RESULTS_FALLBACK
        )

    def get_product_count(self) -> int:
        return len(
            self.get_product_elements()
        )

    # ================================================================
    # PRODUCT NAME
    # ================================================================

    def get_first_product_name(self) -> str:

        products = self.get_product_elements()

        if not products:
            return ""

        product = products[0]

        try:
            return product.find_element(
                *self.PRODUCT_NAME
            ).text.strip()

        except Exception:

            try:

                links = product.find_elements(
                    By.XPATH,
                    ".//h4//a"
                )

                if links:
                    return links[0].text.strip()

            except Exception:
                pass

        return ""

    # ================================================================
    # ADD TO CART
    # ================================================================

    def _find_add_to_cart_button(self, product):

        # Main OpenCart locator
        try:
            return product.find_element(
                *self.ADD_TO_CART_BUTTON
            )
        except NoSuchElementException:
            pass

        # Fallback
        try:
            return product.find_element(
                *self.ADD_TO_CART_BUTTON_FALLBACK
            )
        except NoSuchElementException:
            pass

        # Last fallback: button whose title contains Add
        buttons = product.find_elements(
            By.TAG_NAME,
            "button"
        )

        for button in buttons:

            text = (
                button.text
                or ""
            ).lower()

            title = (
                button.get_attribute(
                    "data-original-title"
                )
                or ""
            ).lower()

            onclick = (
                button.get_attribute(
                    "onclick"
                )
                or ""
            ).lower()

            if (
                "add to cart" in text
                or "add to cart" in title
                or "cart.add" in onclick
            ):
                return button

        raise NoSuchElementException(
            "Add to Cart button not found."
        )

    def click_add_to_cart_first_result(self):

        products = self.get_product_elements()

        if not products:
            raise AssertionError(
                "No search result available "
                "to add to cart."
            )

        product = products[0]

        product_name = self.get_first_product_name()

        print(
            f"\n  🛒  Adding product to cart: "
            f"{product_name}"
        )

        button = self._find_add_to_cart_button(
            product
        )

        self.scroll_into_view(button)

        # JS click avoids overlay/interception problems.
        self.driver.execute_script(
            "arguments[0].click();",
            button
        )

        # Wait briefly for OpenCart AJAX request.
        time.sleep(1.5)

        print(
            "  🛒  Add-to-cart action completed."
        )

    # ================================================================
    # CART STATUS
    # ================================================================

    def get_cart_total_text(self) -> str:

        try:

            return self.driver.find_element(
                *self.CART_TOTAL
            ).text.strip()

        except Exception:

            return ""

    def is_cart_non_empty(self) -> bool:

        text = self.get_cart_total_text()

        if not text:
            return False

        lower = text.lower()

        # Typical values:
        # "0 item(s) - $0.00"
        # "1 item(s) - $123.00"
        #
        # Any visible item count > 0 is enough.
        if "0 item" in lower:
            return False

        if "item" in lower:
            return True

        return False

    # ================================================================
    # SUCCESS ALERT
    # ================================================================

    def is_success_alert_visible(
        self,
        timeout: int = 5
    ) -> bool:

        try:

            WebDriverWait(
                self.driver,
                timeout
            ).until(
                EC.visibility_of_element_located(
                    self.SUCCESS_ALERT
                )
            )

            return True

        except TimeoutException:

            return False

    def get_success_message(self) -> str:

        try:

            return self.driver.find_element(
                *self.SUCCESS_ALERT
            ).text.strip()

        except Exception:

            return ""

    # ================================================================
    # FINAL ADD-TO-CART VERIFICATION
    # ================================================================

    def is_product_added(self) -> bool:

        # Method 1: success alert
        if self.is_success_alert_visible(
            timeout=3
        ):
            print(
                "  ✅  Add-to-cart confirmed "
                "by success alert."
            )
            return True

        # Method 2: cart counter
        if self.is_cart_non_empty():

            print(
                "  ✅  Add-to-cart confirmed "
                "by cart counter."
            )
            return True

        print(
            "  ❌  Add-to-cart could not be confirmed."
        )

        return False