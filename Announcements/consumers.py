# coding=utf-8
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework.authtoken.models import Token
from asgiref.sync import sync_to_async
import logging

from .models import Announcement


class DiscordBotAnnouncementConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = "announcement_updates"
        self.room_group_name = "announcement_updates"

        logging.info(f"WebSocket connection attempting to connect to {self.room_group_name}")

        headers = dict(self.scope['headers'])
        token = headers.get(b"authorization", b"Token None").decode("utf-8").split(" ")[1]  # noqa
        valid_token = await sync_to_async(Token.objects.filter(key=token).exists)()
        if not valid_token:
            logging.info(f"WebSocket connection rejected: Invalid token {token}")
            await self.close(3000, "Unauthorized")
        else:
            real_name = await sync_to_async(lambda: Token.objects.get(key=token).user.real_name)()
            logging.info(f"WebSocket connection accepted: User {real_name}")
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        logging.info(f"WebSocket connection closed: {self.channel_name} with code {close_code}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        logging.info(f"WebSocket message received: {content}")
        if content.get("type", None) == "announcement.unpin":
            try:
                announcement = await Announcement.objects.aget(pk=content["announcement_id"])
                announcement.is_pinned = False
                announcement.pin_until = None
                await announcement.asave()
                logging.info(f"Announcement #{announcement.id} is unpinned")
            except Announcement.DoesNotExist:
                logging.warning(f"Announcement #{content['announcement_id']} does not exist.")
                await self.send_json({
                    "error": f"Announcement #{content['announcement_id']} does not exist."
                })

    # handlers

    async def test_message(self, event: dict):
        print(event)
        message = event['text']
        await self.send_json({
            'message': message
        })

    async def announcement_pin(self, event: dict):
        await self.send_json(event)

    async def announcement_unpin(self, event: dict):
        await self.send_json(event)

    async def announcement_announce(self, event: dict):
        await self.send_json(event)

    async def announcement_delete(self, event: dict):
        await self.send_json(event)
