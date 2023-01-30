"""
Generate Weibo comments and submit.
Click LIKE for each submitted comment.
"""
import json
import logging
import random
from datetime import datetime
from multiprocessing import Queue
from string import ascii_lowercase
from time import sleep

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(processName)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log.log", "w"),
        logging.StreamHandler()
    ]
)
logger_comment_sender = logging.getLogger("CS")
logger_comment_checker = logging.getLogger("CC")


def get_comment_details(weibo_details_index):
    """
    Got the link and the total comments number of the target Weibo.
    :param weibo_details_index: int
    :return: [weibo_link, comments_count]
    """
    with open("resources/data.json", "r") as json_file:
        data = json.load(json_file)
        weibo_link = data["weibo_details"][weibo_details_index]["link"]
        comments_count = data["weibo_details"][weibo_details_index]["comments_count"]
    return [weibo_link, comments_count]


def activate_chrome_driver(account_name):
    """
    Activate Selenium Chrome driver.
    :param account_name: str
    :return: driver
    """
    # get profile name
    with open("resources/accounts.json", "r") as json_file:
        profile = json.load(json_file)[account_name][0]
    # set driver
    options = webdriver.ChromeOptions()
    options.add_argument(r"--user-data-dir=~/Library/Application Support/Google/Chrome")
    options.add_argument(f"--profile-directory={profile}")
    options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    driver.set_window_size(1400, 1000)
    # driver.maximize_window()
    logger_comment_sender.info(f"Chrome driver activate for account {account_name}")
    return driver


def activate_firefox_driver():
    """Activate Selenium Firefox driver."""
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    driver.set_window_size(1400, 1000)
    # driver.maximize_window()
    logger_comment_checker.info("Firefox driver activate")
    return driver


class Login:
    """
    Weibo login.
    """

    def __init__(self, account_name):
        self.account_name = account_name
        self.driver = activate_chrome_driver(account_name)

    def login(self):
        """
        Save login information in Chrome profiles for Weibo Accounts.
        """
        self.driver.implicitly_wait(10)
        self.driver.get("https://weibo.com/login.php")
        self.driver.find_element(
            by=By.XPATH, value="//*[@id='pl_login_form']/div/div[1]/a").click()
        sleep(0.5)
        self.driver.find_element(
            by=By.XPATH, value="//*[@id='pl_login_form']/div/div[1]/a").click()
        # wait for scanning and login
        sleep(20)


class CommentSender:
    """
    Send Weibo comments.
    """

    def __init__(self, account_name, weibo_details_index, check_queue: Queue = None):
        self.account_name = account_name
        self.weibo_details_index = weibo_details_index
        self.check_queue = check_queue
        self.driver = activate_chrome_driver(account_name)

    def send_and_like_comment(self):
        """
        Submit comments and click LIKE for each submitted comment.
        """
        weibo_url = get_comment_details(self.weibo_details_index)[0]
        total_count = get_comment_details(self.weibo_details_index)[1]
        new_comment_count = 0
        timestamp_list = list()
        like = True

        self.driver.get(weibo_url)
        logger_comment_sender.info(f"Chrome driver for account {self.account_name} arrive page {weibo_url}")
        sleep(2)

        # send comments and click like
        with open("resources/accounts.json", "r") as json_file:
            comments_number = json.load(json_file)[self.account_name][1]
        for i in range(comments_number):
            try:
                comment = self.driver.find_element(
                    by=By.XPATH, value="//*[@id='composerEle']/div[2]/div/div[1]/div/textarea")
                # clear the remaining texts before starting a new loop
                if i == 0 and comment.get_attribute("value"):
                    comment.clear()
                # generate comment value
                comment_value = self.generate_random_comment(total_count + 1)
            except NoSuchElementException as e:
                # cookies expired
                logger_comment_sender.error(f"Please log in for account {self.account_name}")
                return None
            submit = self.driver.find_element(
                by=By.XPATH, value="//*[@id='composerEle']/div[2]/div/div[3]/div/button")

            comment.send_keys(comment_value)
            comment.send_keys(Keys.SPACE)
            submit.click()
            sleep(1)
            # check if comment submitted successfully
            _ = self.driver.find_element(
                by=By.XPATH, value="//*[@id='composerEle']/div[2]/div/div[1]/div/textarea")
            submit_flag = False if _.get_attribute("value") else True
            # submission succeeded
            if submit_flag:
                total_count += 1
                new_comment_count += 1
                logger_comment_sender.info(f"Comment #{new_comment_count}: {comment_value}")
                self.update_comment_count(total_count)
                # save the timestamp to check if the comment is valid or not
                timestamp_list.append(comment_value.split()[-1])
                if len(timestamp_list) == 1:
                    # TODO
                    self.check_queue.put(timestamp_list)
                    timestamp_list = list()
                sleep(1)
                if like:
                    like = self.like_comment(new_comment_count)
                    sleep(1)
            # submission failed
            else:
                logger_comment_sender.error("Comment failed, please try again later")
                logger_comment_sender.info(f"{new_comment_count} comments successfully for account "
                                           f"{self.account_name}. {total_count} total for this Weibo.")
                return None
        logger_comment_sender.info(f"{new_comment_count} comments successfully for account "
                                   f"{self.account_name}. {total_count} total for this Weibo.")

    def like_comment(self, new_comment_count, like=True):
        """
        LIKE the comment.
        :param new_comment_count: int
        :param like: bool
        :return: like
        """
        like_button = self.driver.find_element(
            by=By.XPATH,
            value="//*[@id='scroller']/div[1]/div[1]/div/div/div/div[1]/div[2]/div[2]/div[2]/div[4]/button")
        like_button.click()
        sleep(1)
        try:
            like_button.find_element(by=By.CLASS_NAME, value="woo-like-an")
            logger_comment_sender.info(f"LIKE #{new_comment_count}")
        except NoSuchElementException as e:
            # LIKE failed
            like = False
            logger_comment_sender.error(f"Failed to LIKE #{new_comment_count}")
        finally:
            return like

    def update_comment_count(self, total_count):
        """
        Update the total comments number of the target Weibo.
        :param total_count: int
        """
        with open("resources/data.json", "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        data["weibo_details"][self.weibo_details_index]["comments_count"] = total_count
        with open("resources/data.json", "w", encoding="utf-8") as json_file:
            # ensure Chinese characters and JSON format
            json.dump(data, json_file, ensure_ascii=False, indent=2)

    @staticmethod
    def generate_random_comment(count_num):
        """
        Generate comments with random letters and random emojis.
        :param count_num:
        :return: comment string
        """
        timestamp = int(datetime.now().timestamp())
        with open("resources/random_text.txt") as file:
            random_item = random.choice(file.read().splitlines())
        with open("resources/weibo_emoji.txt") as file:
            random_emoji = random.choice(file.read().splitlines())
        random_num = random.randint(1, 14)
        # generate random four letters 2 times, 1 put at the beginning, 2 put after {random_num} words
        random_letters = []
        for i in range(2):
            random_letters.append("".join(random.choice(ascii_lowercase) for x in range(4)))
        return f"{random_letters[0]}{count_num}{random_emoji}{random_item[:random_num]}" \
               f"{random_letters[1]}{random_item[random_num:]} {timestamp}"

    def to_check(self):
        """Build a list of max 5 comments to be checked."""
        # TODO


class CommentChecker:
    """
    Check Weibo comments.
    """

    def __init__(self, weibo_details_index, check_queue: Queue = None):
        self.weibo_details_index = weibo_details_index
        self.check_queue = check_queue
        self.driver = activate_firefox_driver()
        self.timestamp_list = list()

    def get_timestamp_list(self):
        """
        Get timestamp list from Queue.
        """
        while True:
            self.timestamp_list = self.check_queue.get()
            logger_comment_checker.info(self.timestamp_list)

    def check_comments(self):
        """
        Check comments.
        """
        weibo_url = get_comment_details(self.weibo_details_index)[0]

        self.driver.get(weibo_url)
        print(f"Firefox driver go to {weibo_url}")
        sleep(10)

        # check comments
        # click "按时间"
        self.driver.find_element(
            by=By.XPATH,
            value="//*[@id='app']/div[1]/div[2]/div[2]/main/div[1]/div/div[2]/div[2]/div[3]/div/div[1]/div/div[2]"
        ).click()
        sleep(2)
        if "xxx" in self.driver.page_source:
            print("xxx exist")
        else:
            print("Cannot find the text.")
        sleep(2)

        self.driver.close()
        print("====== Firefox Driver Close ======")
