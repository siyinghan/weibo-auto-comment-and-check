"""
Login with different Weibo accounts.
"""
from multiprocessing import Queue, Process

from util import CommentSender, CommentChecker, backup_file, get_start_info

accounts = ["account 1", "account 2", "account 3"]
link_index = 0

if __name__ == "__main__":
    # copy files from the storage
    backup_file("copy")
    get_start_info(accounts, link_index)

    check_queue = Queue()
    p1 = Process(target=CommentSender(accounts, link_index, check_queue).run, args=())
    p2 = Process(target=CommentChecker(link_index, check_queue).run, args=())
    p1.start()
    p2.start()
    p1.join()
    p2.join()

    end()
