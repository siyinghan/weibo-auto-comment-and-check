"""
Login with different Weibo accounts.
"""
import json
import logging
import sys
from multiprocessing import Queue, Process

from util import CommentSender, CommentChecker

accounts = ["account 1", "account 2", "account 3"]
link_index = 0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(processName)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log.log"),
        logging.StreamHandler(stream=sys.stdout)
    ]
)

account_dict = dict()
for account in accounts:
    with open("resources/accounts.json", "r") as json_file:
        comment_num = json.load(json_file)[account][1]
        account_dict[account] = comment_num

if __name__ == "__main__":
    logging.info(f"Start {account_dict}...")

    check_queue = Queue()
    p1 = Process(target=CommentSender(accounts, link_index, check_queue).run, args=())
    p2 = Process(target=CommentChecker(link_index, check_queue).run, args=())
    p1.start()
    p2.start()
    p1.join()
    p2.join()
