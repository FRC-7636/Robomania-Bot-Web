# coding=utf-8
from django.urls import path

from . import consumers


websocket_urlpatterns = [
    path("ws/auth/", consumers.DiscordBotAuthConsumer.as_asgi()),
]
