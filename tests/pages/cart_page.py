"""
tests/pages/cart_page.py

Page Object for the Shopping Cart
Application:
https://tutorialsninja.com/demo/

Responsibilities:
    - Open cart
    - Detect cart product rows
    - Read product name
    - Read/update quantity
    - Read unit price
    - Read row total
    - Verify cart state
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


CART_URL = BASE_URL.rstrip("/") + "/index.php?route=checkout/cart"


class CartPage(BasePage):

    # ================================================================
    # NAVIGATION
    # ================================================================

    CART_BUTTON = (
        By.XPATH,
        "//span[@id='cart-total']/ancestor::button"
    )

    VIEW_CART_LINK = (
        By.XPATH,
        "//a[contains(@href,'checkout/cart')]"
    )

    # ================================================================
    # CART ROWS
    # ================================================================

    # Main locator:
    # A real product row contains a quantity input.
    CART_ROWS = (
        By.XPATH,
        "//input[contains(@name,'quantity')]/ancestor::tr"
    )

    CART_ROWS_FALLBACK = (
        By.XPATH,
        "//table//tbody/tr[.//input[contains(@name,'quantity')]]"
    )

    # ================================================================
    # ROW LOCATORS
    # ================================================================

    PRODUCT_NAME_CELL = (
        By.XPATH,
        ".//td[2]//a"
    )

    QTY_INPUT = (
        By.XPATH,
        ".//input[contains(@name,'quantity')]"
    )

    UPDATE_BTN_PRIMARY = (
        By.XPATH,
        ".//button[@data-original-title='Update']"
    )

    UPDATE_BTN_FALLBACK = (
        By.XPATH,
        ".//button[contains(@onclick,'cart.update')]"
    )

    UNIT_PRICE_CELL = (
        By.XPATH,
        ".//td[5]"
    )

    TOTAL_CELL = (
        By.XPATH,
        ".//td[6]"
    )

    # ================================================================
    # PAGE LOCATORS
    # ================================================================

    EMPTY_CART_MSG = (
        By.XPATH,
        "//*[contains(normalize-space(.),"
        "'Your shopping cart is empty')]"
    )

    SUCCESS_ALERT = (
        By.XPATH,
        "//div[contains(@class,'alert-success')]"
    )

    CART_TABLE = (
        By.XPATH,
        "//table[contains(@class,'table')]"
    )

    # ================================================================
    # NAVIGATION
    # ================================================================

    def go_to_cart(self):
        """
        Directly open cart page.

        Direct navigation is more reliable than depending on the
        cart dropdown animation.
        """

        print("\n  🛒  Opening shopping cart...")

        self.driver.get(CART_URL)

        try:
            WebDriverWait(
                self.driver,
                EXPLICIT_WAIT
            ).until(
                EC.url_contains("checkout/cart")
            )
        except TimeoutException:
            print("  ⚠️  Cart URL wait timed out.")

        # Wait until either:
        #   1. a quantity input appears
        #   2. empty-cart message appears
        try:
            WebDriverWait(
                self.driver,
                EXPLICIT_WAIT
            ).until(
                lambda d: (
                    len(d.find_elements(*self.CART_ROWS)) > 0
                    or
                    len(d.find_elements(*self.EMPTY_CART_MSG)) > 0
                )
            )
        except TimeoutException:
            pass

        time.sleep(0.5)

        print(f"  🛒  Cart URL: {self.driver.current_url}")

    def _go_via_button(self):
        """
        Alternative navigation through cart button.
        """

        try:
            btn = WebDriverWait(
                self.driver,
                EXPLICIT_WAIT
            ).until(
                EC.element_to_be_clickable(
                    self.CART_BUTTON
                )
            )

            self.scroll_into_view(btn)

            btn.click()

            view_link = WebDriverWait(
                self.driver,
                EXPLICIT_WAIT
            ).until(
                EC.element_to_be_clickable(
                    self.VIEW_CART_LINK
                )
            )

            view_link.click()

            WebDriverWait(
                self.driver,
                EXPLICIT_WAIT
            ).until(
                EC.url_contains("checkout/cart")
            )

        except Exception:
            self.driver.get(CART_URL)

    # ================================================================
    # CART ROW METHODS
    # ================================================================

    def get_cart_rows(self):

        # First attempt
        rows = self.driver.find_elements(
            *self.CART_ROWS
        )

        if rows:
            return rows

        # Fallback
        rows = self.driver.find_elements(
            *self.CART_ROWS_FALLBACK
        )

        if rows:
            return rows

        # Diagnostic information
        qty_inputs = self.driver.find_elements(
            By.XPATH,
            "//input[contains(@name,'quantity')]"
        )

        print(
            f"  🔍  Quantity inputs found on page: "
            f"{len(qty_inputs)}"
        )

        empty_message = self.driver.find_elements(
            *self.EMPTY_CART_MSG
        )

        if empty_message:
            print("  🛒  Cart page reports: EMPTY")

        return []

    def get_cart_item_count(self) -> int:
        return len(self.get_cart_rows())

    # ================================================================
    # PRODUCT NAME
    # ================================================================

    def get_first_product_name(self) -> str:

        rows = self.get_cart_rows()

        if not rows:
            return ""

        try:
            name = rows[0].find_element(
                *self.PRODUCT_NAME_CELL
            ).text.strip()

            if name:
                return name

        except (
            NoSuchElementException,
            StaleElementReferenceException
        ):
            pass

        # Generic fallback
        try:
            cells = rows[0].find_elements(
                By.TAG_NAME,
                "td"
            )

            if len(cells) > 1:
                return cells[1].text.strip()

        except Exception:
            pass

        return ""

    # ================================================================
    # QUANTITY
    # ================================================================

    def _find_qty_input(self, row):

        try:
            return row.find_element(
                *self.QTY_INPUT
            )

        except NoSuchElementException:

            inputs = row.find_elements(
                By.TAG_NAME,
                "input"
            )

            for inp in inputs:

                input_type = (
                    inp.get_attribute("type")
                    or ""
                ).lower()

                if input_type in (
                    "",
                    "text",
                    "number"
                ):
                    return inp

            raise NoSuchElementException(
                "Quantity input not found."
            )

    def _find_update_btn(self, row):

        # Primary
        try:
            return row.find_element(
                *self.UPDATE_BTN_PRIMARY
            )
        except NoSuchElementException:
            pass

        # Fallback
        try:
            return row.find_element(
                *self.UPDATE_BTN_FALLBACK
            )
        except NoSuchElementException:
            pass

        # Generic submit button
        buttons = row.find_elements(
            By.XPATH,
            ".//button[@type='submit']"
        )

        if buttons:
            return buttons[0]

        # Any button inside row
        buttons = row.find_elements(
            By.TAG_NAME,
            "button"
        )

        if buttons:
            return buttons[0]

        raise NoSuchElementException(
            "Update button not found."
        )

    def update_quantity(
        self,
        row_index: int = 0,
        quantity: int = 2
    ):

        print(
            f"\n  🛒  Updating cart quantity "
            f"to {quantity}..."
        )

        rows = self.get_cart_rows()

        print(
            f"  🛒  Cart product rows found: "
            f"{len(rows)}"
        )

        if not rows:
            raise AssertionError(
                "Cart is empty. "
                "Cannot update quantity."
            )

        if row_index >= len(rows):
            raise IndexError(
                f"No cart row at index {row_index}. "
                f"Cart contains {len(rows)} row(s)."
            )

        row = rows[row_index]

        qty_input = self._find_qty_input(row)

        self.scroll_into_view(qty_input)

        # Use JavaScript to make sure the input is editable.
        try:
            qty_input.click()
            qty_input.clear()
            qty_input.send_keys(str(quantity))
        except Exception:
            self.driver.execute_script(
                """
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(
                    new Event('change', {bubbles:true})
                );
                """,
                qty_input,
                str(quantity)
            )

        update_btn = self._find_update_btn(row)

        self.scroll_into_view(update_btn)

        # JavaScript click is more reliable on this demo.
        self.driver.execute_script(
            "arguments[0].click();",
            update_btn
        )

        # Give OpenCart time to refresh.
        time.sleep(1.5)

        # Wait for requested quantity.
        try:
            WebDriverWait(
                self.driver,
                EXPLICIT_WAIT
            ).until(
                lambda d:
                self.get_quantity(row_index)
                == str(quantity)
            )

            print(
                f"  ✅  Quantity successfully "
                f"updated to {quantity}"
            )

        except TimeoutException:

            current = self.get_quantity(row_index)

            print(
                f"  ⚠️  Quantity confirmation timeout. "
                f"Current quantity = {current}"
            )

    def get_quantity(
        self,
        row_index: int = 0
    ) -> str:

        rows = self.get_cart_rows()

        if row_index >= len(rows):
            return "0"

        try:
            qty_input = self._find_qty_input(
                rows[row_index]
            )

            return (
                qty_input.get_attribute("value")
                or "0"
            )

        except Exception:
            return "0"

    # ================================================================
    # PRICE
    # ================================================================

    def get_unit_price(
        self,
        row_index: int = 0
    ) -> str:

        rows = self.get_cart_rows()

        if row_index >= len(rows):
            return "$0.00"

        try:
            value = rows[row_index].find_element(
                *self.UNIT_PRICE_CELL
            ).text.strip()

            if value:
                return value

        except Exception:
            pass

        # Generic fallback
        try:
            cells = rows[row_index].find_elements(
                By.TAG_NAME,
                "td"
            )

            if len(cells) > 4:
                return cells[4].text.strip()

        except Exception:
            pass

        return "$0.00"

    # ================================================================
    # ROW TOTAL
    # ================================================================

    def get_row_total(
        self,
        row_index: int = 0
    ) -> str:

        rows = self.get_cart_rows()

        if row_index >= len(rows):
            return "$0.00"

        try:
            value = rows[row_index].find_element(
                *self.TOTAL_CELL
            ).text.strip()

            if value:
                return value

        except Exception:
            pass

        # Generic fallback
        try:
            cells = rows[row_index].find_elements(
                By.TAG_NAME,
                "td"
            )

            if len(cells) > 5:
                return cells[5].text.strip()

        except Exception:
            pass

        return "$0.00"

    # ================================================================
    # CART STATUS
    # ================================================================

    def is_cart_empty(self) -> bool:

        if self.get_cart_item_count() > 0:
            return False

        try:
            return len(
                self.driver.find_elements(
                    *self.EMPTY_CART_MSG
                )
            ) > 0
        except Exception:
            return True

    def is_update_success(self) -> bool:

        try:
            return len(
                self.driver.find_elements(
                    *self.SUCCESS_ALERT
                )
            ) > 0
        except Exception:
            return False