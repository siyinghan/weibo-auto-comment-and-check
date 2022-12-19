"""report"""
from selenium.webdriver.common.by import By

from util import activate_selenium_driver


def extract_links_report_user(url):
    driver = activate_selenium_driver()
    driver.get(url)
    try:
        block = driver.find_element(
            by=By.XPATH, value="//*[@id='plc_main']/div/div/div/div[2]/div[3]")
        element_list = block.find_elements(By.TAG_NAME, "p")
        for i in element_list:
            print(i)

    except Exception as e:
        print(e)
        # return

# def extract_links_report_weibo():
