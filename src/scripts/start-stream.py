from lib.CollectorBot.listener import StreamListener
from utils.logger import logger
from django.conf import settings


def run():
    logger.info('Tweepy stream started')
    stream_listener = StreamListener()
    stream_listener.filter(
        track=[settings.TWITTER_LISTENER_TRACK],
        stall_warnings=True)
