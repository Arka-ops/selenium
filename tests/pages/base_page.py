"""
tests/pages/base_page.py
Base class for all Page Objects.
"""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui        import WebDriverWait
from selenium.webdriver.support           import expected_conditions as EC
from selenium.webdriver.common.by         import By
from selenium.common.exceptions           import TimeoutException

from config.config import EXPLICIT_WAIT


class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver  = driver
        self.wait    = WebDriverWait(driver, EXPLICIT_WAIT)

    # ── Helpers ────────────────────────────────────────────────────────────────

    def find(self, by: By, locator: str):
        return self.wait.until(EC.presence_of_element_located((by, locator)))

    def click(self, by: By, locator: str):
        el = self.wait.until(EC.element_to_be_clickable((by, locator)))
        el.click()
        return el

    def type_text(self, by: By, locator: str, text: str):
        el = self.find(by, locator)
        el.clear()
        el.send_keys(text)
        return el

    def get_text(self, by: By, locator: str) -> str:
        return self.find(by, locator).text.strip()

    def is_visible(self, by: By, locator: str, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, locator))
            )
            return True
        except TimeoutException:
            return False

    def scroll_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    @property
    def title(self) -> str:
        return self.driver.title
