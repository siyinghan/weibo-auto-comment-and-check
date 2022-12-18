import json
import random
import string
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

link_index = 3
account_list = {"汐琊": 20, "太阳": 16, "卷卷": 9, "温妹舔狗": 9, "画画": 9}
account_list1 = {"汐琊": 20, "太阳": 16, "温妹舔狗": 9}


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

    def generate_random_comment(self, random_filename, count_num):
        items = open("{}.txt".format(random_filename)).read().splitlines()
        random_item = random.choice(items)
        weibo_emoji = open("weibo_emoji.txt").read().splitlines()
        random_emoji = random.choice(weibo_emoji)
        random_letters = []
        for i in range(4):
            random_letters.append("".join(random.choice(string.ascii_lowercase) for x in range(4)))
        comment = random_letters[0] + str(count_num) + random_emoji \
                  + random_item[:6] + random_letters[1] + random_item[6:10] \
                  + random_letters[2] + random_item[10:] + " " + random_letters[3]
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
        json_cookies = json.dumps(cookies)
        # will create a new cookies_username.txt file if not exist
        cookies_file = open("cookies_{}.txt".format(username), "w")
        cookies_file.write(json_cookies)

    def send_comments_and_like(self, username, comments_number, random_filename, like=True):
        home_url = "https://weibo.com"
        weibo_url = self.get_comment_details(link_index)[0]
        total_count = self.get_comment_details(link_index)[1]
        new_comment_count = 0

        driver = self.activate_selenium_driver()
        driver.get(home_url)

        # read cookies and login
        cookies = []
        with open("cookies_{}.txt".format(username), "r") as f:
            cookies = json.loads(f.read())
        for cookie in cookies:
            cookie_dict = {
                # "domain": ".weibo.com",
                "name": cookie.get("name"),
                "value": cookie.get("value"),
                "expires": "",
                # "path": "/",
                # "httpOnly": False,
                # "HostOnly": False,
                # "Secure": False
            }
            driver.add_cookie(cookie_dict)
        sleep(6)
        # go to the target weibo
        driver.get(weibo_url)
        sleep(4)

        # send comments and like
        for i in range(comments_number):
            # exit if the stored cookies are expired
            try:
                comment = driver.find_element(
                    by=By.XPATH, value="//*[@id='composerEle']/div[2]/div/div[1]/div/textarea")
            except Exception as e:
                # cookies expired / close the window
                print("Cookies cannot be found (or expired) for {}, please log in again.".format(username))
                print(e)
                return
            submit = driver.find_element(
                by=By.XPATH, value="//*[@id='composerEle']/div[2]/div/div[3]/div/button")

            # exit if the submitting is failed
            if comment.get_attribute("value") != "":
                total_count -= 1
                new_comment_count -= 1
                self.update_comment_count(link_index, total_count)
                print("Left comment failed, please try again later.\nLeft comments {} times successfully for {}."
                      .format(new_comment_count, username))
                return
            # write comment in the textarea
            comment.send_keys(self.generate_random_comment(random_filename, total_count + 1))
            comment.send_keys(Keys.SPACE)
            submit.click()
            total_count += 1
            new_comment_count += 1
            self.update_comment_count(link_index, total_count)
            sleep(3)
            if like:
                # like the comment
                # continue the comments if like is unclickable
                try:
                    like = driver.find_element(
                        by=By.XPATH,
                        value="//*[@id='scroller']/div[1]/div[1]/div/div/div/div[1]/div[2]/div[2]/div[2]/div[4]/button")
                    like.click()
                except Exception as e:
                    print("Like is unclickable.")
                    print(e)
            sleep(2)
        print("Left {} comments successfully for {}. Left {} comments totally."
              .format(new_comment_count, username, total_count))


weibo_auto = WeiboAuto()

# for item in account_list1.items():
#     weibo_auto.send_comments_and_like(item[0], item[1], "表白")

# weibo_auto.save_cookies("画画")

# account_list = {"汐琊": 27, "太阳": 27, "卷卷": 9, "温妹舔狗": 9, "画画": 9}

for item in account_list.items():
    if item[0] == "汐琊":
        weibo_auto.send_comments_and_like(item[0], item[1], "表白")
