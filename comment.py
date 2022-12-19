"""
Generate Weibo comments and submit.
Click LIKE for each submitted comment.
"""
import json
import random
import string
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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


def send_comments_and_like(link_index, username, comments_number, random_filename, like=True):
    """Submit comments and click LIKE for each submitted comment."""
    home_url = "https://weibo.com"
    weibo_url = get_comment_details(link_index)[0]
    total_count = get_comment_details(link_index)[1]
    new_comment_count = 0

    driver = activate_selenium_driver()
    driver.get(home_url)

    # read cookies and login
    try:
        with open("cookies/cookies_{}.txt".format(username), "r") as f:
            cookies = json.loads(f.read())
        for cookie in cookies:
            cookie_dict = {
                # "domain": ".weibo.com",
                "name": cookie.get("name"),
                "value": cookie.get("value"),
                # "expires": "",
                # "path": "/",
                # "httpOnly": False,
                # "HostOnly": False,
                # "Secure": False
            }
            driver.add_cookie(cookie_dict)
    except Exception as e:
        print("Please log in for {}.".format(username))
        print(e)
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
            print("Please log in again for {}.".format(username))
            print(e)
            return
        submit = driver.find_element(
            by=By.XPATH, value="//*[@id='composerEle']/div[2]/div/div[3]/div/button")

        # exit if the submitting is failed
        if comment.get_attribute("value") != "":
            total_count -= 1
            new_comment_count -= 1
            update_comment_count(link_index, total_count)
            print("Left comment failed, please try again later.\nLeft comments {} times successfully for {}."
                  .format(new_comment_count, username))
            return
        # write comment in the textarea
        comment.send_keys(generate_random_comment(random_filename, total_count + 1))
        comment.send_keys(Keys.SPACE)
        submit.click()
        total_count += 1
        new_comment_count += 1
        update_comment_count(link_index, total_count)
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


def activate_selenium_driver():
    """Activate Selenium driver."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.set_window_size(1600, 1000)
    # driver.maximize_window()
    return driver


def get_comment_details(num):
    """Got the link and the total comments number of the target Weibo."""
    data = json.load(open("data.json", "r"))
    link = data["weibo_details"][num]["link"]
    count = data["weibo_details"][num]["comment_count"]
    return [link, count]


def update_comment_count(num, count):
    """Update the total comments number of the target Weibo."""
    data = json.load(open("data.json", "r"))
    data["weibo_details"][num]["comment_count"] = count
    json.dump(data, open("data.json", "w"))


def generate_random_comment(random_filename, count_num):
    """Generate comments with random letters and random emojis."""
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
