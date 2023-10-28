import time
from datetime import datetime

from loguru import logger


def sleep_timer(seconds):
    for i in reversed(range(seconds)):
        time.sleep(1)
        logger.debug(f"Wait {i} sec")


def date_now():
    date_time = datetime.now()
    return date_time.strftime("%Y-%m-%dT%H:%M:%S+03:00")
