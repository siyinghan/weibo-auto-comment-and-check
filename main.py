import json
import random
import string
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# 始发站:泸沽湖
# link = "https://weibo.com/2172061270/MiUOYogZy#comment"
link_num = 0
user_list = {"汐琊": 26, "太阳": 26, "卷卷": 10, "温妹舔狗": 10}
counts = {"12-10-泸沽湖": 0}


class WeiboAuto:
    def get_comment_details(self, num):
        data = json.load(open("data.json", "r"))
        link = data["weibo_details"][num]["link"]
        count = data["weibo_details"][num]["comment_count"]
        return [link, count]

    def update_comment_count(self, num, count):
        data = json.load(open("data.json", "r"))
        data["weibo_details"][num]["comment_count"] = count
        json.dump(data, open("data.json", "w"))

    def generate_random_comment(self, random_filename):
        items = open("{}.txt".format(random_filename)).read().splitlines()
        random_item = random.choice(items)
        random_letters = "".join(random.choice(
            string.ascii_lowercase) for x in range(10))
        comment = random_item + " " + random_letters
        return comment

    def activate_selenium_driver(self):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.set_window_size(1600, 1000)
        # driver.maximize_window()
        return driver

    def save_cookies(self, username):
        login_url = "https://weibo.com/login.php"
        driver = self.activate_selenium_driver()
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
        # will create a new cookies_username.txt file if not exist
        cookies_file = open("cookies_{}.txt".format(username), "w")
        for i in cookies:
            cookies_file.write(str(i))
            cookies_file.write("\n")

    def login_and_send_comments(self, username, comments_number, random_filename):
        home_url = "https://weibo.com"
        weibo_url = self.get_comment_details(link_num)[0]
        count = self.get_comment_details(link_num)[1]
        driver = self.activate_selenium_driver()

        # home_url = "https://weibo.com/login.php"
        driver.get(home_url)
        # read cookies and login
        cookies = []
        with open("cookies_{}.txt".format(username), "r") as f:
            for i in f:
                cookies.append(eval(i.strip()))
        for i in cookies:
            driver.add_cookie(i)
        sleep(8)
        # go to the target weibo
        driver.get(weibo_url)
        sleep(5)
        # write and send comments
        for i in range(comments_number):
            comment = driver.find_element(
                by=By.XPATH, value="//*[@id='composerEle']/div[2]/div/div[1]/div/textarea")
            submit = driver.find_element(
                by=By.XPATH, value="//*[@id='composerEle']/div[2]/div/div[3]/div/button")
            count += 1
            comment.clear()
            comment.send_keys(str(count) + " " + self.generate_random_comment(random_filename))
            comment.send_keys(Keys.SPACE)
            submit.click()
            sleep(3)
        self.update_comment_count(link_num, count)
        # like the recent comments


weibo_auto = WeiboAuto()
for item in user_list.items():
    weibo_auto.login_and_send_comments(item[0], item[1], "表白")
