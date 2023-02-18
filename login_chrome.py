"""
Save login information in the Chrome profile.
"""
from util import Login

# fill in the account name to log in
account_name = "xxx"

if __name__ == "__main__":
    Login().run_chrome(account_name)
