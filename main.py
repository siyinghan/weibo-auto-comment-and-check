"""
Login with different Weibo users.
"""
from comment import send_comments_and_like

account_list = {"汐琊": 20, "太阳": 16, "卷卷": 9, "温妹舔狗": 9, "画画": 9}
account_list1 = {"汐琊": 20, "太阳": 16, "卷卷": 9}

for item in account_list.items():
    send_comments_and_like(3, item[0], item[1], "表白")

# weibo_auto.save_cookies("画画")

# account_list = {"汐琊": 27, "太阳": 27, "卷卷": 9, "温妹舔狗": 9, "画画": 9}

# for item in account_list.items():
#     if item[0] == "汐琊":
#         weibo_auto.send_comments_and_like(3, item[0], item[1], "表白")
