# weibo-auto

## Quickstart

### Preparation

Need to install Chrome and Firefox in advance.

Chrome profile folder:

```zsh
$ open ~/Library/Application\ Support/Google/Chrome
```

Firefox profile folder:

```zsh
$ open ~/Library/Application\ Support/Firefox/Profiles
```

### Chrome Login

1. Create Weibo accounts information file.
    1. Create an empty `json` file in the project **resources** folder.
       ```zsh
       $ touch resources/accounts.json
       ```
    2. Fill in the account names, the accordant profile names,
       and the number that the account can comment (**20** in the example).
       ```json
       {
         "account name 1": [
           "profile name 1",
           20
         ],
         "account name 2": [
           "profile name 2",
           20
         ]
       }
       ```

2. Fill in the `account_name` instead of "xxx" in `login_chrome.py`, then run `login_chrome.py` to log in.
   ```zsh
   $ python login_chrome.py
   ```

3. Scan the QR code in the automated browser to save the login information.

### Firefox Login

1. Open the Firefox folder to get the names of the profile.
   ```zsh
   $ open ~/Library/Application\ Support/Firefox/Profiles
   ```

2. Fill in the `firefox_profile` instead of "colveb6e.default-release" in `util.py`, then run `login_firefox.py`
   to log in.
   ```zsh
   $ python login_firefox.py
   ```

### Create comments data file

1. Create an empty `json` file in the project **resources** folder:
   ```zsh
   $ touch resources/data.json
   ```

2. Add a dictionary in the list of ***weibo_details*** when there is a new Weibo that needs comments.
   Following is the example.
    - ***link***: link to the Weibo
    - ***comment_count***: always put **0** for a new Weibo (will be updated automatically)
    - ***tag***: could be anything
    - ***index***: add **1** every time for a new Weibo

   ```json
   {
     "weibo_details": [
       {
         "link": "",
         "total_comment_count": 0,
         "tag": "",
         "index": 0
       },
       {
         "link": "",
         "total_comment_count": 0,
         "tag": "",
         "index": 1
       }
     ]
   }
   ```

### Send comments and like

1. Replace the account names (should be the same names as in `resources/accounts.json`)
   in `main.py` *accounts = ["account 1", "account 2", "account 3"]*.

2. Start comments and like.
   ```zsh
   $ python main.py
   ```

## Cookie Issue

The Chrome profile (which can be added in Chrome manually) should be used to remain login.

```python
options = webdriver.ChromeOptions()
options.add_argument(r"--user-data-dir=~/Library/Application Support/Google/Chrome")
options.add_argument(rf"--profile-directory={profile}")
driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
```

Another way is to export and save cookies after scanning the QR code, then import cookies to the websites the next time.

Sadly, the cookies should be updated every 24h in this way.

```python
import json

# get cookies and save in the file
all_cookies = driver.get_cookies()
cookies = {}
for item in all_cookies:
    cookies[item["name"]] = item["value"]
    json.dump(cookies, open("cookies/cookies_{}.json".format(username), "w"))

# read cookies and login
driver.get("https://weibo.com")
try:
    cookies = json.load(open("cookies/cookies_{}.json".format(username), "r"))
    for cookie in cookies:
        driver.add_cookie({
            "name": cookie,
            "value": cookies[cookie],
        })
except Exception as e:
    print("Please log in for {}.".format(username))
    print(e)
sleep(6)
```