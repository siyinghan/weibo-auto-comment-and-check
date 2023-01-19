"""
Login with different Weibo accounts.
"""
import json

from util import send_comments_and_like

accounts = ["account 1", "account 2", "account 3"]

for key, value in json.load(open("resources/accounts.json")).items():
    if key in accounts:
        send_comments_and_like(6, key, value[0], value[1])
