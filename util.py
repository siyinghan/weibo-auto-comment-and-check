"""
Generate Weibo comments and submit.
Click LIKE for each submitted comment.
"""
import json
import logging
import random
from datetime import datetime
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
    format="%(asctime)s - %(name)s - %(threadName)s - %(threadName)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log.log", "w"),
        logging.StreamHandler()
    ]
)
logger_comment_sender = logging.getLogger("CS")
logger_comment_checker = logging.getLogger("CC")


class CommentsService:
    """
    Methods for reusing.
    """

    def __init__(self, account_name, weibo_details_index):
        self.account_name = account_name
        self.weibo_details_index = weibo_details_index

    def activate_chrome_driver(self):
        """Activate Selenium Chrome driver."""
        # get profile name
        with open("resources/accounts.json", "r") as json_file:
            profile = json.load(json_file)[self.account_name][0]
        # set driver
        options = webdriver.ChromeOptions()
        options.add_argument(r"--user-data-dir=~/Library/Application Support/Google/Chrome")
        options.add_argument(f"--profile-directory={profile}")
        options.add_argument("--disable-extensions")
        driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
        driver.set_window_size(1400, 1000)
        # driver.maximize_window()
        return driver

    def get_comment_details(self):
        """Got the link and the total comments number of the target Weibo."""
        with open("resources/data.json", "r") as json_file:
            data = json.load(json_file)
            link = data["weibo_details"][self.weibo_details_index]["link"]
            count = data["weibo_details"][self.weibo_details_index]["comments_count"]
        return [link, count]


class Login(CommentsService):
    """
    Weibo login.
    """

    def login(self):
        """Save login information in Chrome profiles for Weibo Accounts."""
        driver = self.activate_chrome_driver()
        driver.implicitly_wait(10)
        driver.get("https://weibo.com/login.php")
        driver.find_element(
            by=By.XPATH, value="//*[@id='pl_login_form']/div/div[1]/a").click()
        sleep(0.5)
        driver.find_element(
            by=By.XPATH, value="//*[@id='pl_login_form']/div/div[1]/a").click()
        # wait for 20s for scanning and login
        sleep(20)


class CommentSender(CommentsService):
    """
    Send Weibo comments.
    """

    def send_comments_and_like(self, like=True):
        """Submit comments and click LIKE for each submitted comment."""
        weibo_url = self.get_comment_details()[0]
        total_count = self.get_comment_details()[1]
        new_comment_count = 0
        pre_comment_value = None

        driver = self.activate_chrome_driver()
        logger_comment_sender.info("====== Chrome driver activate ======")
        driver.get(weibo_url)
        logger_comment_sender.info(f"Chrome driver arrive page {weibo_url}")
        sleep(2)

        # send comments and click like
        logger_comment_sender.info(f"Start leaving comments for {self.account_name} from number {total_count + 1}...")
        with open("resources/accounts.json", "r") as json_file:
            comments_number = json.load(json_file)[self.account_name][1]
        for i in range(comments_number):
            try:
                comment = driver.find_element(
                    by=By.XPATH, value="//*[@id='composerEle']/div[2]/div/div[1]/div/textarea")
                # clear the remaining texts before starting a new loop
                if i == 0 and comment.get_attribute("value"):
                    comment.clear()
                # generate comment value
                comment_value = self.generate_random_comment(total_count + 1)
            except NoSuchElementException as e:
                # cookies expired
                logger_comment_sender.exception(f"Please log in for account {self.account_name}")
                return None
            submit = driver.find_element(
                by=By.XPATH, value="//*[@id='composerEle']/div[2]/div/div[3]/div/button")

            # exit if the submitting is failed
            if comment.get_attribute("value"):
                total_count -= 1
                new_comment_count -= 1
                self.update_comment_count(total_count)
                logger_comment_sender.error("Comment failed, please try again later")
                logger_comment_sender.info(f"{new_comment_count} comments successfully for account "
                                           f"{self.account_name}. {total_count} total for this Weibo.")
                return None

            # log the comment info only after success submitting
            if i > 0 and not comment.get_attribute("value"):
                logger_comment_sender.info(f"Comment #{new_comment_count}: {pre_comment_value}")

            # write comment in the textarea
            comment.send_keys(comment_value)
            pre_comment_value = comment_value
            comment.send_keys(Keys.SPACE)
            submit.click()
            total_count += 1
            new_comment_count += 1
            self.update_comment_count(total_count)
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
        logger_comment_sender.info(f"{new_comment_count} comments successfully for account "
                                   f"{self.account_name}. {total_count} total for this Weibo.")

        driver.close()
        logger_comment_sender.info("====== Chrome Driver Close ======")

    @staticmethod
    def generate_random_comment(count_num):
        """Generate comments with random letters and random emojis."""
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

    def update_comment_count(self, total_count):
        """Update the total comments number of the target Weibo."""
        with open("resources/data.json", "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        data["weibo_details"][self.weibo_details_index]["comments_count"] = total_count
        with open("resources/data.json", "w", encoding="utf-8") as json_file:
            # ensure Chinese characters and JSON format
            json.dump(data, json_file, ensure_ascii=False, indent=2)


class CommentChecker(CommentsService):
    """
    Check Weibo comments.
    """

    @staticmethod
    def activate_firefox_driver():
        """Activate Selenium Firefox driver."""
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        driver.set_window_size(1400, 1000)
        # driver.maximize_window()
        return driver

    def check_comments(self):
        """Check comments."""
        weibo_url = self.get_comment_details()[0]

        driver = self.activate_firefox_driver()
        print("====== Firefox driver activate ======")
        driver.get(weibo_url)
        print(f"Firefox driver go to {weibo_url}")
        sleep(10)

        # check comments
        # click "按时间"
        driver.find_element(
            by=By.XPATH,
            value="//*[@id='app']/div[1]/div[2]/div[2]/main/div[1]/div/div[2]/div[2]/div[3]/div/div[1]/div/div[2]").click()
        sleep(2)
        if "xxx" in driver.page_source:
            print("xxx exist")
        else:
            print("Cannot find the text.")
        sleep(2)

        driver.close()
        print("====== Firefox Driver Close ======")
