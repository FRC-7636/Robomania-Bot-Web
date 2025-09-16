# coding=utf-8
"""
ASGI config for Robomania_Bot_Web project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

import Meetings.routing
import Members.routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Robomania_Bot_Web.settings')

django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(
        Meetings.routing.websocket_urlpatterns + Members.routing.websocket_urlpatterns
    )))
})
