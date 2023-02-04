"""
Login with different Weibo accounts.
"""
from multiprocessing import Queue, Process

from util import CommentSender, CommentChecker, get_start_account_info

accounts = ["account 1", "account 2", "account 3"]
link_index = 0

if __name__ == "__main__":
    get_start_account_info(accounts)

    check_queue = Queue()
    p1 = Process(target=CommentSender(accounts, link_index, check_queue).run, args=())
    p2 = Process(target=CommentChecker(link_index, check_queue).run, args=())
    p1.start()
    p2.start()
    p1.join()
    p2.join()
