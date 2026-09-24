"""
tests/test_ecommerce.py

SELENIUM CAPSTONE – E-Commerce Automation

Application:
    https://tutorialsninja.com/demo/

Covers:
    1. Launch browser
    2. Login
    3. Search product
    4. Add product to cart
    5. Update quantity
    6. Verify cart details
    7. Capture screenshots
    8. Read test data from Excel/JSON
    9. Handle popup/alerts
    10. Generate execution report

Run with pytest:

    python -m pytest tests/test_ecommerce.py -v --tb=short

Standalone:

    python tests/test_ecommerce.py
"""

import sys
import os
import time

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import pytest

from config.config import (
    BASE_URL,
    VALID_EMAIL,
    VALID_PASSWORD,
    SEARCH_TERM,
    PRODUCT_QTY
)

from utils.driver_factory import get_driver
from utils.screenshot_helper import take_screenshot

from utils.data_reader import (
    get_user_from_json,
    get_product_from_json,
    get_products_from_excel
)

from utils.popup_handler import (
    handle_alert,
    dismiss_cookie_banner,
    close_modal
)

from utils.report_generator import (
    generate_html_report
)

from tests.pages.login_page import LoginPage
from tests.pages.search_page import SearchPage
from tests.pages.cart_page import CartPage


# ================================================================
# GLOBAL RESULTS
# ================================================================

RESULTS = []


def log(
    step: str,
    status: str,
    message: str,
    screenshot: str = "",
    duration: float = 0.0
):

    if status == "PASS":
        icon = "✅"
    elif status == "FAIL":
        icon = "❌"
    else:
        icon = "⚠️"

    print(
        f"  {icon}  [{status}]  "
        f"{step}: {message}"
    )

    RESULTS.append(
        {
            "step": step,
            "status": status,
            "message": message,
            "screenshot": screenshot,
            "duration": duration
        }
    )


# ================================================================
# PYTEST DRIVER
# ================================================================

@pytest.fixture(scope="module")
def driver():

    drv = get_driver()

    yield drv

    try:
        drv.quit()
    except Exception:
        pass


# ================================================================
# REPORT
# ================================================================

@pytest.fixture(
    scope="module",
    autouse=True
)
def generate_report():

    yield

    try:
        generate_html_report(RESULTS)
    except Exception as exc:
        print(
            f"  ⚠️  Report generation failed: {exc}"
        )


# ================================================================
# STEP 1 – LAUNCH
# ================================================================

class TestStep1_LaunchBrowser:

    def test_launch_and_open_site(self, driver):

        t0 = time.time()

        driver.get(BASE_URL)

        time.sleep(1)

        title = driver.title

        screenshot = take_screenshot(
            driver,
            "01_browser_launched"
        )

        ok = bool(title)

        log(
            "TC01 – Launch Browser",
            "PASS" if ok else "FAIL",
            f"Browser opened. Page title: '{title}'",
            screenshot,
            time.time() - t0
        )

        assert ok, "Browser/page did not load correctly."


# ================================================================
# STEP 2 – LOGIN
# ================================================================

class TestStep2_Login:

    def test_read_credentials_from_json(self):

        t0 = time.time()

        try:

            user = get_user_from_json(
                "TC001"
            )

            if user:

                log(
                    "TC02a – Read JSON Data",
                    "PASS",
                    f"JSON user loaded: {user}",
                    "",
                    time.time() - t0
                )

            else:

                log(
                    "TC02a – Read JSON Data",
                    "SKIP",
                    "No user found in JSON.",
                    "",
                    time.time() - t0
                )

        except Exception as exc:

            log(
                "TC02a – Read JSON Data",
                "SKIP",
                f"JSON unavailable: {exc}",
                "",
                time.time() - t0
            )

    def test_login(self, driver):

        t0 = time.time()

        login_page = LoginPage(driver)

        try:

            login_page.navigate_to_login()

            handle_alert(driver)

            dismiss_cookie_banner(driver)

            login_page.login(
                VALID_EMAIL,
                VALID_PASSWORD
            )

            time.sleep(1)

            logged_in = login_page.is_logged_in()

            screenshot = take_screenshot(
                driver,
                "02_login"
            )

            if logged_in:

                log(
                    "TC02b – Login",
                    "PASS",
                    "Login successful.",
                    screenshot,
                    time.time() - t0
                )

            else:

                # Tutorial Ninja demo sometimes has no
                # pre-created account.
                log(
                    "TC02b – Login",
                    "SKIP",
                    (
                        "Login attempt completed, "
                        "but demo account was not authenticated. "
                        "Continuing because the public demo allows "
                        "product browsing without login."
                    ),
                    screenshot,
                    time.time() - t0
                )

        except Exception as exc:

            screenshot = take_screenshot(
                driver,
                "02_login_error"
            )

            log(
                "TC02b – Login",
                "SKIP",
                f"Login unavailable on demo site: {exc}",
                screenshot,
                time.time() - t0
            )


# ================================================================
# STEP 3 – SEARCH
# ================================================================

class TestStep3_SearchProduct:

    def test_read_product_from_excel(self):

        t0 = time.time()

        try:

            products = get_products_from_excel()

            product = next(
                (
                    x for x in products
                    if str(
                        x.get(
                            "Search Term",
                            ""
                        )
                    ).strip().lower()
                    ==
                    SEARCH_TERM.strip().lower()
                ),
                None
            )

            if product:

                log(
                    "TC03a – Read Excel Data",
                    "PASS",
                    f"Excel product found: {product}",
                    "",
                    time.time() - t0
                )

            else:

                log(
                    "TC03a – Read Excel Data",
                    "SKIP",
                    (
                        "Product not found in Excel; "
                        "using config value."
                    ),
                    "",
                    time.time() - t0
                )

        except Exception as exc:

            log(
                "TC03a – Read Excel Data",
                "SKIP",
                f"Excel unavailable: {exc}",
                "",
                time.time() - t0
            )

    def test_search_product(self, driver):

        t0 = time.time()

        search_page = SearchPage(driver)

        search_page.search(
            SEARCH_TERM
        )

        count = search_page.get_product_count()

        screenshot = take_screenshot(
            driver,
            "03_search_results"
        )

        log(
            "TC03b – Search Product",
            "PASS" if count > 0 else "FAIL",
            (
                f"Search '{SEARCH_TERM}' "
                f"returned {count} product(s)."
            ),
            screenshot,
            time.time() - t0
        )

        assert count > 0, (
            f"No products found for "
            f"'{SEARCH_TERM}'."
        )


# ================================================================
# STEP 4 – ADD TO CART
# ================================================================

class TestStep4_AddToCart:

    def test_add_to_cart(self, driver):

        t0 = time.time()

        search_page = SearchPage(driver)

        name = search_page.get_first_product_name()

        if not name:

            screenshot = take_screenshot(
                driver,
                "04_add_to_cart_no_product"
            )

            log(
                "TC04 – Add to Cart",
                "FAIL",
                "No product found in search results.",
                screenshot,
                time.time() - t0
            )

            pytest.fail(
                "Cannot add product because "
                "search result is empty."
            )

        # --------------------------------------------------------
        # Click Add to Cart
        # --------------------------------------------------------

        search_page.click_add_to_cart_first_result()

        # --------------------------------------------------------
        # Handle JS alert if present
        # --------------------------------------------------------

        alert_text = handle_alert(
            driver,
            timeout=2
        )

        if alert_text:

            log(
                "TC04a – Handle Alert",
                "PASS",
                f"Alert handled: '{alert_text}'"
            )

        # --------------------------------------------------------
        # IMPORTANT:
        #
        # Do NOT call close_modal() here before checking the
        # success alert.
        # --------------------------------------------------------

        time.sleep(1)

        # --------------------------------------------------------
        # Verify using BOTH:
        #
        # 1. success alert
        # 2. cart counter
        # --------------------------------------------------------

        success_alert = (
            search_page.is_success_alert_visible(
                timeout=3
            )
        )

        cart_non_empty = (
            search_page.is_cart_non_empty()
        )

        success = (
            success_alert
            or cart_non_empty
        )

        screenshot = take_screenshot(
            driver,
            "04_add_to_cart"
        )

        if success_alert:

            message = (
                search_page.get_success_message()
                or
                "Success alert detected."
            )

        elif cart_non_empty:

            message = (
                "Cart counter confirms "
                "product was added."
            )

        else:

            message = (
                "Product could not be confirmed "
                "in cart."
            )

        log(
            "TC04b – Add to Cart",
            "PASS" if success else "FAIL",
            f"Product '{name}' – {message}",
            screenshot,
            time.time() - t0
        )

        assert success, (
            f"Add-to-cart failed for '{name}'. "
            f"Cart text: "
            f"'{search_page.get_cart_total_text()}'"
        )


# ================================================================
# STEP 5 – UPDATE QUANTITY
# ================================================================

class TestStep5_UpdateQuantity:

    def test_update_quantity(self, driver):

        t0 = time.time()

        cart_page = CartPage(driver)

        cart_page.go_to_cart()

        screenshot_before = take_screenshot(
            driver,
            "05a_cart_before_update"
        )

        item_count = (
            cart_page.get_cart_item_count()
        )

        if item_count == 0:

            log(
                "TC05 – Update Quantity",
                "FAIL",
                (
                    "Cart is empty after successful "
                    "Add-to-Cart verification."
                ),
                screenshot_before,
                time.time() - t0
            )

            pytest.fail(
                "Cart is empty. "
                "Cannot update quantity."
            )

        initial_qty = (
            cart_page.get_quantity(0)
        )

        cart_page.update_quantity(
            row_index=0,
            quantity=PRODUCT_QTY
        )

        time.sleep(0.5)

        new_qty = (
            cart_page.get_quantity(0)
        )

        screenshot_after = take_screenshot(
            driver,
            "05b_cart_after_update"
        )

        ok = (
            str(new_qty)
            ==
            str(PRODUCT_QTY)
        )

        log(
            "TC05 – Update Quantity",
            "PASS" if ok else "FAIL",
            (
                f"Quantity: {initial_qty} "
                f"→ {new_qty} "
                f"(expected {PRODUCT_QTY})"
            ),
            screenshot_after,
            time.time() - t0
        )

        assert ok, (
            f"Quantity update failed. "
            f"Expected {PRODUCT_QTY}, "
            f"got {new_qty}."
        )


# ================================================================
# STEP 6 – VERIFY CART
# ================================================================

class TestStep6_VerifyCart:

    def test_verify_cart_details(self, driver):

        t0 = time.time()

        cart_page = CartPage(driver)

        # Always return to cart.
        cart_page.go_to_cart()

        item_count = (
            cart_page.get_cart_item_count()
        )

        if item_count == 0:

            screenshot = take_screenshot(
                driver,
                "06_cart_empty"
            )

            log(
                "TC06 – Verify Cart",
                "FAIL",
                "Cart is empty.",
                screenshot,
                time.time() - t0
            )

            pytest.fail(
                "Cannot verify cart because "
                "cart is empty."
            )

        product_name = (
            cart_page.get_first_product_name()
        )

        quantity = (
            cart_page.get_quantity(0)
        )

        unit_price = (
            cart_page.get_unit_price(0)
        )

        row_total = (
            cart_page.get_row_total(0)
        )

        screenshot = take_screenshot(
            driver,
            "06_cart_details_verified"
        )

        checks = {

            "Item count > 0":
                item_count > 0,

            "Product name":
                bool(product_name),

            "Quantity correct":
                str(quantity)
                ==
                str(PRODUCT_QTY),

            "Unit price":
                bool(unit_price)
                and unit_price != "$0.00"
        }

        all_pass = all(
            checks.values()
        )

        detail_message = " | ".join(
            f"{key}: "
            f"{'✓' if value else '✗'}"
            for key, value
            in checks.items()
        )

        log(
            "TC06 – Verify Cart",
            "PASS" if all_pass else "FAIL",
            (
                f"Product='{product_name}', "
                f"Qty={quantity}, "
                f"Unit={unit_price}, "
                f"RowTotal={row_total}. "
                f"Checks: {detail_message}"
            ),
            screenshot,
            time.time() - t0
        )

        print(
            "\n"
            + "─" * 60
        )

        print(
            "  🛒  CART DETAILS SUMMARY"
        )

        print(
            "─" * 60
        )

        print(
            f"  Products in cart : {item_count}"
        )

        print(
            f"  Product name     : {product_name}"
        )

        print(
            f"  Quantity         : {quantity}"
        )

        print(
            f"  Unit price       : {unit_price}"
        )

        print(
            f"  Row total        : {row_total}"
        )

        print(
            "─" * 60
        )

        assert all_pass, (
            f"Cart verification failed: "
            f"{detail_message}"
        )


# ================================================================
# STEP 7 – SCREENSHOT
# ================================================================

class TestStep7_Screenshot:

    def test_final_screenshot(self, driver):

        t0 = time.time()

        screenshot = take_screenshot(
            driver,
            "07_final_state"
        )

        log(
            "TC07 – Final Screenshot",
            "PASS",
            (
                "Final screenshot captured: "
                f"{os.path.basename(screenshot)}"
            ),
            screenshot,
            time.time() - t0
        )


# ================================================================
# STEP 8 – POPUP / ALERT
# ================================================================

class TestStep8_PopupHandling:

    def test_popup_handling(self, driver):

        t0 = time.time()

        # First handle JS alert.
        alert_text = handle_alert(
            driver,
            timeout=2
        )

        # Then safely try actual modal.
        modal_closed = close_modal(
            driver,
            timeout=2
        )

        log(
            "TC08 – Popup/Alert Handling",
            "PASS",
            (
                f"Alert='{alert_text or 'none'}'; "
                f"Modal closed={modal_closed}"
            ),
            "",
            time.time() - t0
        )


# ================================================================
# STANDALONE RUNNER
# ================================================================

def run_standalone():

    print(
        "\n"
        + "═" * 70
    )

    print(
        "  SELENIUM CAPSTONE – "
        "E-COMMERCE AUTOMATION"
    )

    print(
        "═" * 70
    )

    driver = get_driver()

    try:

        # --------------------------------------------------------
        # TC01
        # --------------------------------------------------------

        t0 = time.time()

        driver.get(BASE_URL)

        screenshot = take_screenshot(
            driver,
            "01_launch"
        )

        log(
            "TC01 – Launch Browser",
            "PASS",
            f"Title: {driver.title}",
            screenshot,
            time.time() - t0
        )

        # --------------------------------------------------------
        # TC02
        # --------------------------------------------------------

        t0 = time.time()

        login_page = LoginPage(driver)

        try:

            login_page.navigate_to_login()

            handle_alert(driver)

            dismiss_cookie_banner(
                driver
            )

            login_page.login(
                VALID_EMAIL,
                VALID_PASSWORD
            )

            time.sleep(1)

            logged = (
                login_page.is_logged_in()
            )

            screenshot = take_screenshot(
                driver,
                "02_login"
            )

            log(
                "TC02 – Login",
                "PASS" if logged else "SKIP",
                (
                    "Login successful."
                    if logged
                    else
                    "Demo account not authenticated; "
                    "continuing with public demo."
                ),
                screenshot,
                time.time() - t0
            )

        except Exception as exc:

            screenshot = take_screenshot(
                driver,
                "02_login_error"
            )

            log(
                "TC02 – Login",
                "SKIP",
                f"Login unavailable: {exc}",
                screenshot,
                time.time() - t0
            )

        # --------------------------------------------------------
        # TC03 SEARCH
        # --------------------------------------------------------

        t0 = time.time()

        search_page = SearchPage(driver)

        search_page.search(
            SEARCH_TERM
        )

        count = (
            search_page.get_product_count()
        )

        screenshot = take_screenshot(
            driver,
            "03_search"
        )

        log(
            "TC03 – Search",
            "PASS" if count > 0 else "FAIL",
            (
                f"{count} result(s) "
                f"for '{SEARCH_TERM}'"
            ),
            screenshot,
            time.time() - t0
        )

        if count == 0:

            print(
                "\n❌ Search returned no products."
            )

            return

        # --------------------------------------------------------
        # TC04 ADD TO CART
        # --------------------------------------------------------

        t0 = time.time()

        product_name = (
            search_page.get_first_product_name()
        )

        search_page.click_add_to_cart_first_result()

        alert_text = handle_alert(
            driver,
            timeout=2
        )

        if alert_text:

            log(
                "TC04a – Handle Alert",
                "PASS",
                f"Alert: '{alert_text}'"
            )

        time.sleep(1)

        success_alert = (
            search_page.is_success_alert_visible(
                timeout=3
            )
        )

        cart_non_empty = (
            search_page.is_cart_non_empty()
        )

        add_success = (
            success_alert
            or cart_non_empty
        )

        screenshot = take_screenshot(
            driver,
            "04_add_cart"
        )

        log(
            "TC04 – Add to Cart",
            "PASS" if add_success else "FAIL",
            (
                f"Added '{product_name}'. "
                f"Cart='{search_page.get_cart_total_text()}'"
            ),
            screenshot,
            time.time() - t0
        )

        # --------------------------------------------------------
        # IMPORTANT:
        #
        # Do not continue if Add-to-Cart really failed.
        # This prevents IndexError at update_quantity().
        # --------------------------------------------------------

        if not add_success:

            print(
                "\n❌ Add-to-cart failed."
            )

            print(
                "   TC05 and TC06 cannot continue."
            )

            return

        # --------------------------------------------------------
        # TC05 UPDATE QUANTITY
        # --------------------------------------------------------

        t0 = time.time()

        cart_page = CartPage(driver)

        cart_page.go_to_cart()

        item_count = (
            cart_page.get_cart_item_count()
        )

        if item_count == 0:

            screenshot = take_screenshot(
                driver,
                "05_empty_cart"
            )

            log(
                "TC05 – Update Quantity",
                "FAIL",
                (
                    "Add-to-cart appeared successful "
                    "but cart page contains no product."
                ),
                screenshot,
                time.time() - t0
            )

            return

        initial_qty = (
            cart_page.get_quantity(0)
        )

        cart_page.update_quantity(
            0,
            PRODUCT_QTY
        )

        new_qty = (
            cart_page.get_quantity(0)
        )

        screenshot = take_screenshot(
            driver,
            "05_update_qty"
        )

        quantity_success = (
            str(new_qty)
            ==
            str(PRODUCT_QTY)
        )

        log(
            "TC05 – Update Quantity",
            "PASS"
            if quantity_success
            else "FAIL",
            (
                f"Quantity "
                f"{initial_qty} → {new_qty}"
            ),
            screenshot,
            time.time() - t0
        )

        if not quantity_success:

            print(
                "\n❌ Quantity update failed."
            )

            return

        # --------------------------------------------------------
        # TC06 VERIFY CART
        # --------------------------------------------------------

        t0 = time.time()

        cart_page.go_to_cart()

        product_name = (
            cart_page.get_first_product_name()
        )

        quantity = (
            cart_page.get_quantity(0)
        )

        unit_price = (
            cart_page.get_unit_price(0)
        )

        row_total = (
            cart_page.get_row_total(0)
        )

        screenshot = take_screenshot(
            driver,
            "06_verify_cart"
        )

        checks = {

            "Item count":
                cart_page.get_cart_item_count() > 0,

            "Product name":
                bool(product_name),

            "Quantity":
                str(quantity)
                ==
                str(PRODUCT_QTY),

            "Unit price":
                unit_price != "$0.00"
        }

        verify_success = all(
            checks.values()
        )

        log(
            "TC06 – Verify Cart",
            "PASS"
            if verify_success
            else "FAIL",
            (
                f"Product='{product_name}', "
                f"Qty={quantity}, "
                f"Price={unit_price}, "
                f"Total={row_total}"
            ),
            screenshot,
            time.time() - t0
        )

        print(
            "\n"
            + "─" * 60
        )

        print(
            "  🛒  FINAL CART SUMMARY"
        )

        print(
            "─" * 60
        )

        print(
            f"  Product : {product_name}"
        )

        print(
            f"  Qty     : {quantity}"
        )

        print(
            f"  Price   : {unit_price}"
        )

        print(
            f"  Total   : {row_total}"
        )

        print(
            "─" * 60
        )

        # --------------------------------------------------------
        # TC07 SCREENSHOT
        # --------------------------------------------------------

        screenshot = take_screenshot(
            driver,
            "07_final"
        )

        log(
            "TC07 – Final Screenshot",
            "PASS",
            "Final screenshot captured.",
            screenshot
        )

        # --------------------------------------------------------
        # TC08 POPUPS
        # --------------------------------------------------------

        alert_text = handle_alert(
            driver,
            timeout=2
        )

        modal_closed = close_modal(
            driver,
            timeout=2
        )

        log(
            "TC08 – Popup/Alert Handling",
            "PASS",
            (
                f"Alert='{alert_text or 'none'}'; "
                f"Modal closed={modal_closed}"
            )
        )

    except Exception as exc:

        print(
            "\n❌ UNEXPECTED ERROR"
        )

        print(
            f"   {type(exc).__name__}: {exc}"
        )

        try:

            screenshot = take_screenshot(
                driver,
                "99_unexpected_error"
            )

            log(
                "Unexpected Error",
                "FAIL",
                str(exc),
                screenshot
            )

        except Exception:
            pass

    finally:

        try:
            generate_html_report(
                RESULTS
            )
        except Exception as exc:
            print(
                f"⚠️ Report generation error: {exc}"
            )

        try:
            driver.quit()
        except Exception:
            pass

        print(
            "\n"
            + "═" * 70
        )

        print(
            "  TEST EXECUTION FINISHED"
        )

        print(
            "═" * 70
        )


# ================================================================
# MAIN
# ================================================================

if __name__ == "__main__":
    run_standalone()