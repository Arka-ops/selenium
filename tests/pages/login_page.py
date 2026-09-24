"""
tests/pages/login_page.py
Page Object for the Login / Account pages on tutorialsninja.com/demo/
"""

from selenium.webdriver.common.by import By
from .base_page                   import BasePage


class LoginPage(BasePage):
    # ── Locators ───────────────────────────────────────────────────────────────
    MY_ACCOUNT_MENU   = (By.XPATH, "//span[text()='My Account']")
    LOGIN_MENU_ITEM   = (By.XPATH, "//a[text()='Login']")
    EMAIL_INPUT       = (By.ID,    "input-email")
    PASSWORD_INPUT    = (By.ID,    "input-password")
    LOGIN_BUTTON      = (By.XPATH, "//input[@value='Login']")
    LOGOUT_LINK       = (By.XPATH, "//a[contains(text(),'Logout')]")
    ERROR_MESSAGE     = (By.XPATH, "//div[contains(@class,'alert-danger')]")
    MY_ACCOUNT_HEADING= (By.XPATH, "//h2[text()='My Account']")

    # ── Actions ────────────────────────────────────────────────────────────────

    def navigate_to_login(self):
        self.click(*self.MY_ACCOUNT_MENU)
        self.click(*self.LOGIN_MENU_ITEM)

    def login(self, email: str, password: str):
        self.type_text(*self.EMAIL_INPUT,    email)
        self.type_text(*self.PASSWORD_INPUT, password)
        self.click(*self.LOGIN_BUTTON)

    def is_logged_in(self) -> bool:
        return self.is_visible(*self.LOGOUT_LINK, timeout=5)

    def get_error_message(self) -> str:
        return self.get_text(*self.ERROR_MESSAGE)
