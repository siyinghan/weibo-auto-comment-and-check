"""Save Cookies."""
import json
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def save_cookies(username):
    """Save login information for Weibo Users."""
    login_url = "https://weibo.com/login.php"
    driver = activate_selenium_driver()
    driver.implicitly_wait(10)
    driver.get(login_url)
    driver.find_element(
        by=By.XPATH, value="//*[@id='pl_login_form']/div/div[1]/a").click()
    sleep(0.5)
    driver.find_element(
        by=By.XPATH, value="//*[@id='pl_login_form']/div/div[1]/a").click()
    # wait for 20s for scanning and login
    sleep(20)
    # get cookies and save in the file
    cookies = driver.get_cookies()
    json_cookies = json.dumps(cookies)
    # will create a new cookies_username.txt file if not exist
    cookies_file = open("cookies/cookies_{}.txt".format(username), "w")
    cookies_file.write(json_cookies)


def activate_selenium_driver():
    """Activate Selenium driver."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.set_window_size(1600, 1000)
    # driver.maximize_window()
    return driver
