"""
Login with different Weibo accounts.
"""
import json
import os
from multiprocessing import Pool

from util import SendComments

# accounts = ["汐琊", "太阳", "温妹舔狗"]
accounts = ["汐琊"]

if __name__ == "__main__":
    SendComments("汐琊", 7).send_comments_and_like()

# if __name__ == "__main__":
#     pool = Pool(processes=2)
#     pool.apply_async(check_comments, args=(7,))
#
#     for key, value in json.load(open("resources/accounts.json")).items():
#         if key in accounts:
#             args = (7, key, value[0], value[1])
#             pool.apply_async(send_comments_and_like, args)
#             # sleep(10)
#
#     pool.close()
#     pool.join()
