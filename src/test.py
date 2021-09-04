"""
    get_random.py

    MediaWiki API Demos
    Demo of `Random` module: Get request to list 5 random pages.

    MIT License
"""

import requests

S = requests.Session()

URL = "https://en.wikipedia.org/w/api.php"

PARAMS = {
    "action": "query",
    "format": "json",
    "list": "random",
    "rnlimit": "5",
    "rnnamespace": "0",
    "maxlag": "1"
}

R = S.get(url=URL, params=PARAMS)
DATA = R.json()

RANDOMS = DATA["query"]["random"]

for r in RANDOMS:
    print(r["title"])
