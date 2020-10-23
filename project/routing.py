from channels.routing import ProtocolTypeRouter,URLRouter
from django.conf.urls import url
from users.consumers import PostConsumer
from channels.auth import AuthMiddlewareStack
application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
    URLRouter([
            url(r"^ws/blog/$", PostConsumer),
            
        ])
    ),
})



