"""
Login with different Weibo users.
"""
from util import save_cookies, send_comments_and_like

account_list = {
    "汐琊": ["Default", 26],
    "太阳": ["Profile 7", 20],
    "卷卷": ["Profile 8", 9],
    "温妹舔狗": ["Profile 9", 9],
    "画画": ["Profile 10", 9],
}

user = ["汐琊", "太阳", "温妹舔狗"]

for key, value in account_list.items():
    if key in user:
        send_comments_and_like(5, key, value[0], value[1], "表白")

# save_cookies(user, account_list[user][0])

# extract_links_report_user("太阳", "https://weibo.com/ttarticle/p/show?id=2309404848364541051167")
