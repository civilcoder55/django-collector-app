from celery import shared_task
from lib.CollectorBot.handler import Handler
from utils.logger import logger


@shared_task(serializer='pickle')
def add_status_to_queue(status):
    Handler.handle_collection(status)
    logger.info(f"status id:{status.id} processed")
