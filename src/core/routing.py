from .consumers import NotificationConsumer
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'ws/notifier/$', NotificationConsumer.as_asgi()),
]
