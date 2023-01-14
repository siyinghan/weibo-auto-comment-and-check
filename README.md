# weibo-auto

chrome path: ```~/Library/Application\ Support/Google/Chrome```

```json
{
  "weibo_details": [
    {
      "link": "weibo_link1",
      "comment_count": 1,
      "tag": "",
      "index": 0
    },
    {
      "link": "weibo_link2",
      "comment_count": 1,
      "tag": "",
      "index": 1
    }
  ]
}
```

## Cookie
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