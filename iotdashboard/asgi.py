import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from consumers import RealTimeConsumer
from django.urls import path, re_path

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VideoChat.settings')

application = ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        'websocket': URLRouter([re_path("real-time/$", RealTimeConsumer.as_asgi())]),
        # 'websocket': AllowedHostsOriginValidator(
        #     AuthMiddlewareStack(URLRouter(routing.application))
        # )
        
    }
)