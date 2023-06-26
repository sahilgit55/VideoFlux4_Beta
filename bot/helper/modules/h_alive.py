from requests import get
from threading import Timer

from bot import BASE_URL, LOGGER

def keep_alive():
    LOGGER.info(f"🔶Heroku Keep Alive: [{BASE_URL}] - {get(BASE_URL).status_code}")


if len(BASE_URL) and "herokuapp.com" in BASE_URL:
    Timer(600, keep_alive()).start()