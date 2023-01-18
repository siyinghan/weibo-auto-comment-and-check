# weibo-auto

## Quickstart

### Login

1. Create new profiles in Chrome manually.

2. Open the Chrome folder to get the names of new profiles:
    ```zsh
    $ open ~/Library/Application\ Support/Google/Chrome
    ```

3. Add the profile name in `login.py` and run ```python login.py``` to save the login information.

### Create accounts information file

1. Create an empty `json` file:
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

### Create comments data file

1. Create an empty `json` file:
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
         "comment_count": 0,
         "tag": "",
         "index": 0
       },
       {
         "link": "",
         "comment_count": 0,
         "tag": "",
         "index": 1
       }
     ]
   }
   ```

### Send comments and like

1. Replace the account names (should be the same names as in `resources/accounts.json`)
   in `main.py` *accounts = ["account 1", "account 2", "account 3"]*.

2. Start comments and like by running ```python main.py```.

## Cookie Issue

The Chrome profile (which can be added in Chrome manually) should be used to remain login.

```python
options = webdriver.ChromeOptions()
options.add_argument(r"--user-data-dir=~/Library/Application Support/Google/Chrome")
options.add_argument("--profile-directory={}".format(profile))
driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
```

Here is another way: export and save cookies after scanning, then import cookies to the websites the next time.
The cookies should be updated every 24h in this way.

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