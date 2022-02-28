from lib.CollectorBot.listener import StreamListener
from utils.logger import logger

def run():
    logger.info('Tweepy stream started')
    stream_listener = StreamListener()
    stream_listener.filter(track=['@_collectorapp_'], stall_warnings=True)
