"""
Login with different Weibo accounts.
"""
from multiprocessing import Queue, Process

from util import CommentSender, CommentChecker

accounts = ["account 1", "account 2", "account 3"]

if __name__ == "__main__":
    check_queue = Queue()
    p1 = Process(target=CommentSender(accounts, 7, check_queue).run, args=())
    p2 = Process(target=CommentChecker(7, check_queue).run, args=())
    p1.start()
    p2.start()
    p1.join()
    p2.join()
