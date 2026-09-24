"""
utils/driver_factory.py
Creates and returns a configured WebDriver instance.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service  import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service    import Service as EdgeService
from selenium.webdriver.chrome.options  import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome  import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from config.config import BROWSER, HEADLESS, IMPLICIT_WAIT


def get_driver() -> webdriver.Remote:
    """Instantiate the WebDriver based on config settings."""
    browser = BROWSER.lower()

    if browser == "chrome":
        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        opts.add_argument("--disable-notifications")
        opts.add_argument("--disable-popup-blocking")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        if HEADLESS:
            opts.add_argument("--headless=new")
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=opts
        )

    elif browser == "firefox":
        opts = FirefoxOptions()
        if HEADLESS:
            opts.add_argument("--headless")
        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=opts
        )

    elif browser == "edge":
        driver = webdriver.Edge(
            service=EdgeService(EdgeChromiumDriverManager().install())
        )

    else:
        raise ValueError(f"Unsupported browser: {BROWSER}")

    driver.implicitly_wait(IMPLICIT_WAIT)
    return driver
