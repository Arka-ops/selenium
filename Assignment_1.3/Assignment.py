# ============================================================
# ASSIGNMENT 1
# Basic Selenium Locators
# ID, NAME, TAG_NAME, CLASS_NAME and LINK_TEXT
# ============================================================

import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Launch Chrome
driver = webdriver.Chrome()

# Open website
driver.get("https://testautomationpractice.blogspot.com/")

# Locate element using ID
driver.find_element(By.ID, "name").send_keys("Arka Pan")

# Locate element using NAME
driver.find_element(By.NAME, "input1").send_keys("Very Good")

# Locate element using TAG_NAME
driver.find_element(By.TAG_NAME, "input").clear()

# Locate element using CLASS_NAME
driver.find_element(By.CLASS_NAME, "form-check-input").click()

# Locate element using LINK_TEXT
driver.find_element(By.LINK_TEXT, "Udemy Courses").click()

# Wait for a few seconds
time.sleep(5)

# Close browser
driver.quit()


# ============================================================
# ASSIGNMENT 2
# Locate All Links Using TAG_NAME
# ============================================================

'''
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Launch Chrome
driver = webdriver.Chrome()

# Open website
driver.get("https://testautomationpractice.blogspot.com/")

# Locate all <a> elements
elements = driver.find_elements(By.TAG_NAME, "a")

# Print the text of each link
for element in elements:
    print(element.text)

time.sleep(2)

# Close browser
driver.quit()
'''


# ============================================================
# ASSIGNMENT 3
# CSS Selector with Wildcard
# Locate elements whose ID starts with a particular value
# ============================================================

'''
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Launch Chrome
driver = webdriver.Chrome()

# Open website
driver.get("https://testautomationpractice.blogspot.com/")

# Locate elements whose ID starts with "a"
elements = driver.find_elements(
    By.CSS_SELECTOR,
    "*[id^='a']"
)

# Print the text of each element
for element in elements:
    print(element.text)

time.sleep(2)

# Close browser
driver.quit()
'''


# ============================================================
# ASSIGNMENT 4
# CSS Child Selectors
# Locate elements using the direct-child (>) selector
# ============================================================

'''
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Launch Chrome
driver = webdriver.Chrome()

# Open website
driver.get("https://testautomationpractice.blogspot.com/")

# Locate input using CSS child selector
driver.find_element(
    By.CSS_SELECTOR,
    "div.form-group > input.form-control"
).send_keys("Chiranjit")

# Locate Udemy Courses using CSS child selector
driver.find_element(
    By.CSS_SELECTOR,
    "div.widget-content > ul > li > a[href*='udemy']"
).click()

time.sleep(2)

# Close browser
driver.quit()
'''
