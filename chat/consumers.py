import json
import sys
from datetime import datetime, timedelta

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
import logging
import redis.asyncio as redis
from chat.models import Room

User = get_user_model()

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.RATE_LIMIT_INTERVAL = timedelta(seconds=1)

        if not self.scope["user"].is_authenticated:
            await self.close()
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        try:
            room_exists = await sync_to_async(Room.objects.filter(id=self.room_id).exists)()
            if not room_exists:
                logger.info(f"User {self.scope['user'].id} tried to connect to non-existent room {self.room_id}.")
                await self.close()
            self.redis_client = await redis.from_url('redis://redis:6379', decode_responses=True)

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            logger.info(f"User {self.scope['user'].id} connected to room {self.room_id}.")

            await self.send_last_messages()
        except Exception as e:
            logger.error(f"Error during connection: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"User {self.scope['user'].id} disconnected from room {self.room_id}.")
        except Exception as e:
            logger.error(f"Error during disconnection: {e}")

        if hasattr(self, 'redis_client'):
            await self.redis_client.close()

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            user = self.scope['user']
            if not await self.is_allowed_to_send_message(user.id):
                logger.info(f"User {user.id} is rate-limited and tried to send a message.")
                await self.send(text_data=json.dumps({
                    'error': 'You are sending messages too quickly. Please wait a moment.'
                }))
                return

            message_data = {
                'user_id': user.id,
                'user_first_name': user.first_name,
                'user_last_name': user.last_name,
                'content': message,
                'timestamp': self.get_current_timestamp()
            }
            if 'test' in sys.argv:
                redis_key = f'room_{self.room_id}_messages_test'
            else:
                redis_key = f'room_{self.room_id}_messages'
            await self.redis_client.rpush(redis_key, json.dumps(message_data))
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_first_name': user.first_name,
                    'user_last_name': user.last_name,
                    'user_id': user.id,
                }
            )

            await self.store_last_message_timestamp(user.id)
            logger.info(f"User {user.id} sent a message in room {self.room_id}.")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
        except Exception as e:
            logger.error(f"Error during message receipt: {e}")

    async def chat_message(self, event):
        try:
            message = event['message']
            user_first_name = event['user_first_name']
            user_last_name = event['user_last_name']

            await self.send(text_data=json.dumps({
                'message': message,
                'user_first_name': user_first_name,
                'user_last_name': user_last_name,
                'user_id': event['user_id'],
            }))
        except Exception as e:
            logger.error(f"Error during sending chat message: {e}")

    def get_current_timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()

    async def send_last_messages(self):
        try:
            messages = await self.redis_client.lrange(f'room_{self.room_id}_messages', 0, -1)
            for message in messages:
                message_data = json.loads(message)
                await self.send(text_data=json.dumps({
                    'user_id': message_data['user_id'],
                    'message': message_data['content'],
                    'user_first_name': message_data['user_first_name'],
                    'user_last_name': message_data['user_last_name'],
                }))
        except Exception as e:
            logger.error(f"Error during sending last messages: {e}")

    async def is_allowed_to_send_message(self, user_id):
        try:
            last_message_timestamp = await self.redis_client.get(f'user_{user_id}_last_message_timestamp')
            if last_message_timestamp:
                last_message_time = datetime.fromisoformat(last_message_timestamp)
                if datetime.now() - last_message_time < self.RATE_LIMIT_INTERVAL:
                    return False
            return True
        except Exception as e:
            logger.error(f"Error during rate limiting check: {e}")
            return False

    async def store_last_message_timestamp(self, user_id):
        try:
            await self.redis_client.set(
                f'user_{user_id}_last_message_timestamp',
                datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Error during storing last message timestamp: {e}")
