from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = UiAutomator2Options().load_capabilities({
    "platformName": "Android", "automationName": "UiAutomator2",
    "appPackage": "com.example.app", "appActivity": ".MainActivity"
})
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.ID, "com.example.app:id/email"))).send_keys("qa@example.test")
    driver.find_element(By.ID, "com.example.app:id/password").send_keys("test-password")
    driver.find_element(By.ACCESSIBILITY_ID, "Sign in").click()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.ACCESSIBILITY_ID, "Dashboard")))
finally:
    driver.quit()
