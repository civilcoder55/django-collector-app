from core import consumers
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'ws/notifier/', consumers.PostConsumer.as_asgi()),
]
