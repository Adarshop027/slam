import requests
from bot import SHORTENER, SHORTENER_API
import random
import base64
from urllib.parse import quote
import pyshorteners
from urllib3 import disable_warnings


def short_url(longurl):
    if SHORTENER == "shorte.st" and SHORTENER_API is not None:
        disable_warnings()
        return requests.get(f'http://api.{SHORTENER}/stxt/{SHORTENER_API}/{longurl}', verify=False).text
    elif "linkvertise" in SHORTENER and SHORTENER_API is not None:
        url = quote(base64.b64encode(longurl.encode("utf-8")))
        linkvertise = [
            f"https://link-to.net/{SHORTENER_API}/{random.random() * 1000}/dynamic?r={url}",
            f"https://up-to-down.net/{SHORTENER_API}/{random.random() * 1000}/dynamic?r={url}",
            f"https://direct-link.net/{SHORTENER_API}/{random.random() * 1000}/dynamic?r={url}",
            f"https://file-link.net/{SHORTENER_API}/{random.random() * 1000}/dynamic?r={url}"]
        return random.choice(linkvertise)
    elif "bitly" in SHORTENER and SHORTENER_API is not None:
        s = pyshorteners.Shortener(api_key=SHORTENER_API)
        bitly = s.bitly.short(longurl)
        return bitly
    else:
        return requests.get(f'https://{SHORTENER}/api?api={SHORTENER_API}&url={longurl}&format=text').text