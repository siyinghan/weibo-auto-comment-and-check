"""
Login with different Weibo accounts.
"""
import json

from util import send_comments_and_like

accounts = ["account 1", "account 2", "account 3"]

for key, value in json.load(open("resources/accounts.json")).items():
    if key in accounts:
        # leave comments without clicking the LIKE button
        send_comments_and_like(link_index=0, account_name=key, profile=value[0], comments_number=value[1], like=False)
