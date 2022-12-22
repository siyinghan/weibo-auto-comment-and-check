"""
Login with different Weibo users.
"""
from util import save_cookies, send_comments_and_like

account_list = {"汐琊": 20, "太阳": 20, "卷卷": 9, "温妹舔狗": 9, "画画": 9}
account_list1 = {"汐琊": 20, "太阳": 20, "卷卷": 9}

for item in account_list1.items():
    send_comments_and_like(4, item[0], item[1], "表白")

# save_cookies("太阳")

# account_list = {"汐琊": 27, "太阳": 27, "卷卷": 9, "温妹舔狗": 9, "画画": 9}

# for item in account_list.items():
#     if item[0] == "汐琊":
#         send_comments_and_like(4, item[0], item[1], "表白", False)

# extract_links_report_user("https://weibo.com/ttarticle/p/show?id=2309404847982506803627")
