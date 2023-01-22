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


def login(profile):
    """Save login information in Chrome profiles for Weibo Accounts."""
    driver = activate_selenium_driver(profile)
    driver.implicitly_wait(10)
    driver.get("https://weibo.com/login.php")
    driver.find_element(
        by=By.XPATH, value="//*[@id='pl_login_form']/div/div[1]/a").click()
    sleep(0.5)
    driver.find_element(
        by=By.XPATH, value="//*[@id='pl_login_form']/div/div[1]/a").click()
    # wait for 20s for scanning and login
    sleep(20)


def send_comments_and_like(link_index, account_name, profile, comments_number, like=True):
    """Submit comments and click LIKE for each submitted comment."""
    weibo_url = get_comment_details(link_index)[0]
    total_count = get_comment_details(link_index)[1]
    new_comment_count = 0

    driver = activate_selenium_driver(profile)
    driver.get(weibo_url)
    sleep(4)

    print("Start leaving comments for {} from number {}..."
          .format(account_name, total_count + 1))

    # send comments and click like
    for i in range(comments_number):
        # exit if the stored cookies are expired
        try:
            comment = driver.find_element(
                by=By.XPATH, value="//*[@id='composerEle']/div[2]/div/div[1]/div/textarea")
        except Exception as e:
            # cookies expired / close the window
            print("Please log in again for {}.".format(account_name))
            print(e)
            return
        submit = driver.find_element(
            by=By.XPATH, value="//*[@id='composerEle']/div[2]/div/div[3]/div/button")

        # clear the remaining texts before starting a new loop
        if new_comment_count == 0:
            comment.clear()

        # exit if the submitting is failed
        if comment.get_attribute("value") != "":
            total_count -= 1
            new_comment_count -= 1
            update_comment_count(link_index, total_count)
            print("Left comment failed, please try again later.\n"
                  "Left comments {} times successfully for {}. Total comments number {}.\n"
                  .format(new_comment_count, account_name, total_count))
            return
        # write comment in the textarea
        comment.send_keys(generate_random_comment(total_count + 1))
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
    print("Left {} comments successfully for {}. Total comments number {}.\n"
          .format(new_comment_count, account_name, total_count))


def activate_selenium_driver(profile):
    """Activate Selenium driver."""
    options = webdriver.ChromeOptions()
    options.add_argument(r"--user-data-dir=~/Library/Application Support/Google/Chrome")
    options.add_argument("--profile-directory={}".format(profile))
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    driver.set_window_size(1600, 1000)
    # driver.maximize_window()
    return driver


def get_comment_details(num):
    """Got the link and the total comments number of the target Weibo."""
    data = json.load(open("resources/data.json", "r"))
    link = data["weibo_details"][num]["link"]
    count = data["weibo_details"][num]["comment_count"]
    return [link, count]


def update_comment_count(num, count):
    """Update the total comments number of the target Weibo."""
    data = json.load(open("resources/data.json", "r"))
    data["weibo_details"][num]["comment_count"] = count
    json.dump(data, open("resources/data.json", "w"))


def generate_random_comment(count_num):
    """Generate comments with random letters and random emojis."""
    items = open("resources/random_text.txt").read().splitlines()
    random_item = random.choice(items)
    weibo_emoji = open("resources/weibo_emoji.txt").read().splitlines()
    random_emoji = random.choice(weibo_emoji)
    random_num = random.randint(1, 12)
    # generate random four letters 3 times, 1 put at the beginning, 2 put after a {random_num} words, 3 put at the end
    random_letters = []
    for i in range(3):
        random_letters.append("".join(random.choice(string.ascii_lowercase) for x in range(4)))
    comment = random_letters[0] + str(count_num) + random_emoji \
              + random_item[:random_num] + random_letters[1] \
              + random_item[random_num:] + " " + random_letters[2]
    return comment
