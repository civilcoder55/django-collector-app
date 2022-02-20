import time

import tweepy
from core.tasks import add_status_to_queue
from django.conf import settings
from utils.logger import logger


class StreamListener(tweepy.Stream):

    def __init__(self):
        super().__init__(**settings.TWITTER_SECRETS)

    def on_status(self, status):
        if 'collect' in status.text.lower().split(" "):
            add_status_to_queue.delay(status)
            logger.info(f"New mention added to worker queue")

    def on_error(self, status_code):
        logger.error(f"Tweepy stream has error with statusCode:{status_code}")
        if status_code == 420:
            time.sleep(60)
            return True
