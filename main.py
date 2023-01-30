"""
Login with different Weibo accounts.
"""
import json
from multiprocessing import Pool, Queue, Process

from util import CommentSender, CommentChecker, activate_chrome_driver, activate_firefox_driver

# accounts = ["汐琊", "太阳", "温妹舔狗"]
accounts = ["太阳"]


# if __name__ == "__main__":
#     for account in accounts:
#         CommentSender(account, 7).send_and_like_comment()

def send(q):
    """
    Send comments.
    :param q: multiprocessing.Queue
    """
    comment_sender = CommentSender("汐琊", 7, check_queue=q)
    comment_sender.send_and_like_comment()


def check(q):
    """
    Check comments.
    :param q: multiprocessing.Queue
    """
    comment_checker = CommentChecker(7, check_queue=q)
    comment_checker.get_timestamp_list()


if __name__ == "__main__":
    check_queue = Queue()
    # comment_sender = CommentSender("太阳", 7, check_queue)
    # comment_checker = CommentChecker(7, check_queue)

    p1 = Process(target=send, args=(check_queue,))
    p2 = Process(target=check, args=(check_queue,))

    # p1 = Process(target=activate_chrome_driver, args=("太阳",))
    # p2 = Process(target=activate_firefox_driver, args=())
    p1.start()
    p2.start()
    p1.join()
    p2.join()

    # pool = Pool(processes=2)
    #
    # pool.apply(activate_chrome_driver, args=("太阳",))
    # pool.apply(activate_firefox_driver, args=())
    #
    # # for key, value in json.load(open("resources/accounts.json")).items():
    # #     if key in accounts:
    # #         args = (7, key, value[0], value[1])
    # #         pool.apply_async(CommentSender("太阳", 7, check_queue).send_and_like_comment, args)
    # #         # sleep(10)
    #
    # pool.close()
    # pool.join()
