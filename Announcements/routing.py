# coding=utf-8
from django.urls import path

from . import consumers


websocket_urlpatterns = [
    path("ws/announcement/", consumers.DiscordBotAnnouncementConsumer.as_asgi()),
]
