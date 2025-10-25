# coding=utf-8
from django.dispatch import Signal
from django.conf import settings
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework.authtoken.models import Token
from asgiref.sync import sync_to_async
import logging
from json import dump


role_update_signal, channel_update_signal = Signal(), Signal()


class DiscordBotMeetingConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = "meeting_updates"
        self.room_group_name = "meeting_updates"

        logging.info(
            f"WebSocket connection attempting to connect to {self.room_group_name}"
        )

        headers = dict(self.scope["headers"])
        token = (
            headers.get(b"authorization", b"Token None").decode("utf-8").split(" ")[1]  # noqa
        )
        valid_token = await sync_to_async(Token.objects.filter(key=token).exists)()
        if not valid_token and not self.scope["user"].has_perm(
            ["Meetings.add_meetingsignin", "Meetings.change_meetingsignin"]
        ):
            logging.info(f"WebSocket connection rejected: Invalid token {token} and user")
            await self.close(3000, "Unauthorized")
        else:
            if not valid_token:
                real_name = self.scope["user"].real_name
            else:
                real_name = await sync_to_async(
                    lambda: Token.objects.get(key=token).user.real_name
                )()
            logging.info(f"WebSocket connection accepted: User {real_name}")
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            # Request initial roles and channels data
            await self.send_json({"type": "meeting.request_initial_data"})

    async def disconnect(self, close_code):
        logging.info(
            f"WebSocket connection closed: {self.channel_name} with code {close_code}"
        )
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        logging.info(f"WebSocket message received: {content}")
        if content.get("type") == "roles_update":
            await role_update_signal.asend(self.__class__, roles=content.get("roles", []))
            with open(settings.BASE_DIR / "roles.json", "w") as f:
                dump(content.get("roles", []), f, indent=4)
        elif content.get("type") == "channels_update":
            await channel_update_signal.asend(self.__class__, channels=content.get("channels", []))
            with open(settings.BASE_DIR / "channels.json", "w") as f:
                dump(content.get("channels", []), f, indent=4)

    # handlers

    async def test_message(self, event: dict):
        print(event)
        message = event["text"]
        await self.send_json({"message": message})

    async def meeting_edit(self, event: dict):
        await self.send_json(event)

    async def meeting_create(self, event: dict):
        await self.send_json(event)

    async def meeting_delete(self, event: dict):
        await self.send_json(event)

    async def meeting_new_absent_request(self, event: dict):
        await self.send_json(event)

    async def meeting_review_absent_request(self, event: dict):
        await self.send_json(event)

    async def meeting_request_initial_data(self, event: dict):
        await self.send_json(event)


class WebSignInConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["uuid"]
        self.room_group_name = f"meeting_signin_{self.room_name}"

        logging.info(
            f"WebSocket connection attempting to connect to {self.room_group_name}"
        )
        if not self.scope["user"].has_perm(
                ["Meetings.add_meetingsignin", "Meetings.change_meetingsignin"]
        ):
            logging.info(f"WebSocket connection rejected: Invalid user")
            await self.close(3000, "Unauthorized")
        else:
            real_name = self.scope["user"].real_name
            logging.info(f"WebSocket connection accepted: User {real_name}")
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        logging.info(
            f"WebSocket connection closed: {self.channel_name} with code {close_code}"
        )
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        logging.info(f"WebSocket message received: {content}")

    # handlers

    async def signin_new_record(self, event: dict):
        await self.send_json(event)
