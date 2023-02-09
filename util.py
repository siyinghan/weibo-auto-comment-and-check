"""
Generate Weibo comments and submit.
Click LIKE for each submitted comment.
"""
import json
import logging
import os.path
import random
import re
import sys
from datetime import datetime
from multiprocessing import Queue
from shutil import copy
from string import ascii_lowercase
from time import sleep

from pathlib import Path
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

# create "log" folder if it is not exist
os.makedirs("log", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(processName)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("./log/weibo-auto.log"),
        logging.StreamHandler(stream=sys.stdout)
    ]
)
logger_comment_sender = logging.getLogger("CS")
logger_comment_checker = logging.getLogger("CC")


def get_start_info(account_names, link_index):
    """
    Log the running accounts information.
    :param account_names: List[str]
    :param link_index: int
    """
    # copy files from the storage
    backup_file("copy")

    account_dict = dict()
    with open("conf/accounts.json", "r") as json_file:
        data = json.load(json_file)
        for account_name in account_names:
            comment_num = data[account_name][1]
            account_dict[account_name] = comment_num
    with open("conf/data.json", "r") as json_file:
        data = json.load(json_file)
        weibo_tag = data["weibo_details"][link_index]["tag"]
        total_comment_count = data["weibo_details"][link_index]["total_comment_count"]
    logging.info(f"Start {account_dict} | {{'{weibo_tag}': {total_comment_count}}} ...")

    # save start info in the file
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("./log/visibility_rate.log", "a", encoding="utf-8") as file:
        file.write(f"{time} - Start {account_dict} | {{'{weibo_tag}': {total_comment_count}}}\r")


def end():
    """
    Back up files in the end.
    """
    # backup files to the storage
    backup_file("backup")


def backup_file(action):
    """
    Copy the configuration and the log files to storage for safety.
    :param action: "copy" or "backup"
    """
    project_dir = Path(__file__).parent.absolute()
    storage_dir = "/Volumes/home/Project/weibo-auto"
    copy_file = ["accounts.json", "data.json", "visibility_rate.log"]
    for filename in copy_file:
        conf_path = os.path.join(project_dir, "conf", filename)
        log_path = os.path.join(project_dir, "log", filename)
        storage_path = os.path.join(storage_dir, filename)
        if action == "copy":
            if filename.endswith(".log"):
                try:
                    copy(storage_path, log_path)
                    logger_comment_sender.info(f"Copy '{filename}'")
                except FileNotFoundError as _:
                    logger_comment_sender.error("Fail to copy {filename}'")
            elif filename == "accounts.json":
                if not os.path.join(Path(__file__).parent.absolute(), "conf/accounts.json"):
                    try:
                        copy(storage_path, conf_path)
                        logger_comment_sender.info(f"Copy '{filename}'")
                    except FileNotFoundError as _:
                        logger_comment_sender.error("Fail to copy {filename}'")
            else:
                try:
                    copy(storage_path, conf_path)
                    logger_comment_sender.info(f"Copy '{filename}'")
                except FileNotFoundError as _:
                    logger_comment_sender.error("Fail to copy {filename}'")
        if action == "backup":
            if filename.endswith(".log"):
                try:
                    copy(log_path, storage_path)
                    logger_comment_sender.info(f"Backup '{filename}'")
                except FileNotFoundError as _:
                    logger_comment_sender.error("Fail to backup {filename}'")
            elif filename.endswith(".json"):
                try:
                    copy(conf_path, storage_path)
                    logger_comment_sender.info(f"Backup '{filename}'")
                except FileNotFoundError as _:
                    logger_comment_sender.error("Fail to backup {filename}'")


def get_comment_details(weibo_details_index):
    """
    Got the link and the total comments number of the target Weibo.
    :param weibo_details_index: int
    :return: [str, int]
    """
    with open("conf/data.json", "r") as json_file:
        data = json.load(json_file)
        weibo_link = data["weibo_details"][weibo_details_index]["link"]
        total_comment_count = data["weibo_details"][weibo_details_index]["total_comment_count"]
    return [weibo_link, total_comment_count]


def activate_chrome_driver(account_name):
    """
    Activate Selenium Chrome driver.
    :param account_name: str
    :return: driver
    """
    # get profile name
    with open("conf/accounts.json", "r") as json_file:
        profile = json.load(json_file)[account_name][0]
    # set driver
    options = webdriver.ChromeOptions()
    options.add_argument(r"--user-data-dir=~/Library/Application Support/Google/Chrome")
    options.add_argument(rf"--profile-directory={profile}")
    options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    driver.set_window_size(1400, 1000)
    return driver


def activate_firefox_driver():
    """Activate Selenium Firefox driver."""
    firefox_location = os.path.expanduser(r"~/Library/Application Support/Firefox/Profiles")
    firefox_profile = [_ for _ in os.listdir(firefox_location) if _.endswith("release")][0]
    driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()),
        firefox_profile=webdriver.FirefoxProfile(os.path.join(firefox_location, firefox_profile)))
    driver.set_window_size(1400, 1000)
    return driver


class Login:
    """
    Weibo login.
    """

    def run_chrome(self, account_name):
        """
        Chrome login.
        """
        with activate_chrome_driver(account_name) as driver:
            self.login(driver)

    def run_firefox(self):
        """
        Firefox login.
        """
        with activate_firefox_driver() as driver:
            self.login(driver)

    @staticmethod
    def login(driver):
        """
        Save login information in Chrome profiles for Weibo Accounts.
        """
        driver.implicitly_wait(10)
        driver.get("https://weibo.com/login.php")
        driver.find_element(
            by=By.XPATH, value="//*[@id='pl_login_form']/div/div[1]/a").click()
        sleep(0.5)
        driver.find_element(
            by=By.XPATH, value="//*[@id='pl_login_form']/div/div[1]/a").click()
        # wait for scanning and login
        sleep(20)


class CommentSender:
    """
    Send Weibo comments.
    """

    def __init__(self, account_names, weibo_details_index, check_queue):
        self.account_names = account_names
        self.weibo_details_index = weibo_details_index
        self.check_queue = check_queue
        self.like = True
        self.driver = None
        self.account_name = None
        self.new_comment_count = 0
        self.account_comment_num = 0
        self.weibo_url = get_comment_details(self.weibo_details_index)[0]
        self.total_comment_count = get_comment_details(self.weibo_details_index)[1]

    def run(self):
        """
        Run comment sender.
        """

        for account_name in self.account_names:
            self.account_name = account_name
            self.new_comment_count = 0

            with open("conf/accounts.json", "r") as json_file:
                self.account_comment_num = json.load(json_file)[account_name][1]

            with activate_chrome_driver(self.account_name) as driver:
                self.driver = driver
                logger_comment_sender.info(f"Chrome driver is activated with account '{self.account_name}'")
                self.send_and_like_comment()

            # set LIKE to True for the next account
            self.like = True

        self.check_queue.put("All Done")
        logger_comment_sender.debug("Put 'All Done' in Queue")

    def send_and_like_comment(self):
        """
        Go to the target Weibo.
        Input the comment and submit it.
        LIKE the comment.
        """

        self.driver.get(self.weibo_url)
        logger_comment_sender.info(f"Open (send comments - '{self.account_name}'): {self.weibo_url}")
        sleep(4)

        # send comments and click like
        for i in range(self.account_comment_num):
            try:
                comment = self.driver.find_element(
                    by=By.XPATH, value="//*[@id='composerEle']/div[2]/div/div[1]/div/textarea")
                # clear the remaining texts before starting a new loop
                if i == 0 and comment.get_attribute("value"):
                    comment.clear()
                # generate comment value
                generate_comment = self.generate_random_comment(self.total_comment_count + 1)
                comment_value = generate_comment[0]
                comment_timestamp = generate_comment[1]
                comment_num = self.total_comment_count + 1
            except NoSuchElementException as _:
                # cookies expired
                logger_comment_sender.error(f"Please log in for account {self.account_name}")
                return None
            submit = self.driver.find_element(
                by=By.XPATH, value="//*[@id='composerEle']/div[2]/div/div[3]/div/button")

            comment.send_keys(comment_value)
            comment.send_keys(Keys.SPACE)
            submit.click()
            sleep(2)

            # check if comment submitted successfully
            _ = self.driver.find_element(by=By.XPATH, value="//*[@id='composerEle']/div[2]/div/div[1]/div/textarea")
            submit_flag = False if _.get_attribute("value") else True
            # submission succeeded
            if submit_flag:
                self.total_comment_count += 1
                self.new_comment_count += 1
                self.update_comment_count()
                logger_comment_sender.info(f"'{self.account_name}' #{self.new_comment_count}: '{comment_value}'")
                # save the timestamp to check if the comment is valid or not
                self.check_queue.put(f"{comment_num} {comment_timestamp}")
                logger_comment_sender.debug(f"Put '{comment_num} {comment_timestamp}' in Queue")
                sleep(1)
                if self.like:
                    self.like_comment(self.driver)
                    sleep(1)
            # submission failed
            else:
                logger_comment_sender.error("Comment failed, please try again later")
                break

        self.check_queue.put(f"Done {self.account_name} {self.total_comment_count}")
        logger_comment_sender.info(f"Put 'Done {self.account_name} {self.total_comment_count}' in Queue")

    def like_comment(self, driver):
        """
        LIKE the comment. Stop LIKE when it's not clickable.
        """
        like_button = driver.find_element(
            by=By.XPATH,
            value="//*[@id='scroller']/div[1]/div[1]/div/div/div/div[1]/div[2]/div[2]/div[2]/div[4]/button")
        like_button.click()
        sleep(1)
        try:
            like_button.find_element(by=By.CLASS_NAME, value="woo-like-an")
            logger_comment_sender.info(f"LIKE #{self.total_comment_count}")
        except NoSuchElementException as _:
            # LIKE failed
            self.like = False
            logger_comment_sender.warning(f"Failed to LIKE comment #{self.total_comment_count}")

    def update_comment_count(self):
        """
        Update the total comments number of the target Weibo.
        """
        with open("conf/data.json", "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        data["weibo_details"][self.weibo_details_index]["total_comment_count"] = self.total_comment_count
        with open("conf/data.json", "w", encoding="utf-8") as json_file:
            # ensure Chinese characters and JSON format
            json.dump(data, json_file, ensure_ascii=False, indent=2)

    @staticmethod
    def generate_random_comment(count_num):
        """
        Generate comments with random letters and random emojis.
        :param count_num: int
        :return: str
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
            random_letters.append("".join(random.choice(ascii_lowercase) for _ in range(4)))
        comment = f"{random_letters[0]}{count_num}{random_emoji}{random_item[:random_num]}" \
                  f"{random_letters[1]}{random_item[random_num:]} t{timestamp}"
        return [comment, timestamp]


class CommentChecker:
    """
    Check Weibo comments.
    """

    def __init__(self, weibo_details_index, check_queue: Queue = None):
        self.weibo_details_index = weibo_details_index
        self.check_queue = check_queue
        self.driver = None
        self.submit_comment_count = 0
        self.visible_comment_count = 0
        self.visible_comment = set()
        self.one_account_comment = dict()
        self.comment_check = dict()
        self.accounts_check_summary = dict()

    def run(self):
        """
        Run comment sender.
        """
        with activate_firefox_driver() as driver:
            self.driver = driver
            logger_comment_checker.info("Firefox driver is activated")
            self.check_comments()

    def check_comments(self):
        """
        Check comments.
        """
        weibo_url = get_comment_details(self.weibo_details_index)[0]

        self.driver.get(weibo_url)
        logger_comment_checker.info(f"Open (check comments): {weibo_url}")

        while True:
            get_item = self.check_queue.get()
            logger_comment_checker.debug(f"Get '{get_item}' from Queue")

            # one account finished
            if get_item.startswith("Done"):
                self.one_account_comment_done(get_item)
            # all accounts finished
            elif get_item.startswith("All"):
                self.all_accounts_comment_done()
                break
            # one comment submitted
            else:
                self.one_comment_submit(get_item)

    def one_comment_submit(self, get_item):
        """
        Update variables and get timestamps from the page when CommentSender submitted a comment.
        :param get_item: str from Queue
        """
        self.submit_comment_count += 1
        comment_num = get_item.split()[0]
        comment_timestamp = get_item.split()[1]
        self.one_account_comment[comment_timestamp] = comment_num
        # set comment_num default to False
        self.comment_check[comment_num] = False
        self.get_page_timestamp()

    def one_account_comment_done(self, get_item):
        """
        Check comments visibility and update variables when CommentSender finished sending comments for one account.
        :param get_item: str from Queue
        """
        account_name = get_item.split()[1]
        total_comment_count = get_item.split()[2]
        logger_comment_checker.info(f"'{account_name}' done")

        # check comments visibility of the finished account
        self.check_comment_visibility()

        # calculate visibility_rate only when submit_comment_count is not 0
        if self.submit_comment_count:
            visibility_rate = "{:.2%}".format(self.visible_comment_count / self.submit_comment_count)
            self.accounts_check_summary[account_name] = (
                self.visible_comment_count, self.submit_comment_count, visibility_rate)
            logger_comment_checker.info(f"'{account_name}' - {{send: {self.submit_comment_count}, "
                                        f"visible: {self.visible_comment_count}, visibility rate: {visibility_rate}. "
                                        f"total (this Weibo): {total_comment_count}}}")

        # reset for the next account
        self.submit_comment_count = 0
        self.visible_comment_count = 0
        self.one_account_comment = dict()
        self.comment_check = dict()

    def all_accounts_comment_done(self):
        """
        Log info when CommentSender finished sending comments for all accounts.
        """
        logger_comment_checker.info("All accounts done")
        logger_comment_checker.info(self.accounts_check_summary)

        # save account_summary in the file
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("./log/visibility_rate.log", "a", encoding="utf-8") as file:
            file.write(f"{time} - {self.accounts_check_summary}\r")

    def get_page_timestamp(self):
        """
        Refresh and get all timestamps (starts with "t") from the page.
        """
        sleep(1)

        # click "按时间", sometimes it is not clickable, try another 2 times
        self.driver.find_element(
            by=By.XPATH,
            value="//*[@id='app']/div[1]/div[2]/div[2]/main/div[1]/div/div[2]/div[2]/div[3]/div/div["
                  "1]/div/div[2]"
        ).click()
        sleep(1)

        # get all timestamps that start with "t" from the page
        page_source = self.driver.page_source
        valid_timestamps = set(re.findall("t([0-9]{10})", page_source))
        logger_comment_checker.debug(f"Valid timestamps in the page: {valid_timestamps}")
        for valid_timestamp in valid_timestamps:
            self.visible_comment.add(valid_timestamp)

    def check_comment_visibility(self):
        """
        Check if the submitted comment is visible.
        """
        for comment_timestamp, comment_num in self.one_account_comment.items():
            if comment_timestamp in self.visible_comment:
                # set comment_num to True if comment_timestamp is visible
                self.comment_check[comment_num] = True
        invalid_comment = dict()
        for comment_num, status in self.comment_check.items():
            if not status:
                invalid_comment[comment_num] = status
            else:
                self.visible_comment_count += 1
        logger_comment_checker.info(f"{invalid_comment}")
