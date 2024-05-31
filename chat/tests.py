import json
import asyncio
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import AnonymousUser
import redis.asyncio as redis
from django.test import TestCase
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from django.urls import reverse

from .consumers import ChatConsumer
from .models import Room

User = get_user_model()


class ChatConsumerTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='testuser1', email='testuser1@exampletest.com',
                                             password='password')
        cls.user2 = User.objects.create_user(username='testuser2', email='testuser2@exampletest.com',
                                             password='password')
        cls.room = Room.objects.create()
        cls.room.participants.set([cls.user1, cls.user2])

    async def create_room_with_participants(self, participants):
        room = await sync_to_async(Room.objects.create)()
        await sync_to_async(room.participants.set)(participants)
        return room

    async def test_create_room_with_participants(self):
        room = await self.create_room_with_participants([self.user1, self.user2])
        participants = await sync_to_async(list)(room.participants.all())
        self.assertEqual(participants, [self.user1, self.user2])

    async def get_authenticated_communicator(self, user):
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), f"/ws/chat/{self.room.id}/")
        communicator.scope['user'] = user
        communicator.scope['url_route'] = {'kwargs': {'room_id': self.room.id}}
        return communicator

    async def get_unauthenticated_communicator(self):
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), f"/ws/chat/{self.room.id}/")
        communicator.scope['user'] = AnonymousUser()
        communicator.scope['url_route'] = {'kwargs': {'room_id': self.room.id}}
        return communicator

    async def test_connect_to_existing_room_authenticated(self):
        communicator = await self.get_authenticated_communicator(self.user1)
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_connect_to_existing_room_unauthenticated(self):
        communicator = await self.get_unauthenticated_communicator()
        connected, _ = await communicator.connect()
        self.assertFalse(connected)

    async def test_connect_to_non_existent_room(self):
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat/999/")
        communicator.scope['user'] = self.user1
        communicator.scope['url_route'] = {'kwargs': {'room_id': 999}}
        connected, _ = await communicator.connect()
        self.assertFalse(connected)

    async def test_send_and_receive_message(self):
        communicator = await self.get_authenticated_communicator(self.user1)
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await asyncio.sleep(1)
        message = "Hello world"
        await communicator.send_json_to({
            'message': message
        })

        response = await communicator.receive_json_from()
        self.assertEqual(response['message'], message)
        self.assertEqual(response['user_first_name'], self.user1.first_name)
        self.assertEqual(response['user_last_name'], self.user1.last_name)
        self.assertEqual(response['user_id'], self.user1.id)

        await communicator.disconnect()

    async def test_message_persistence_in_redis(self):
        communicator = await self.get_authenticated_communicator(self.user1)
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await asyncio.sleep(1)
        message = "Hello, Redis"
        await communicator.send_json_to({
            'message': message
        })

        await asyncio.sleep(1)
        redis_client = await redis.from_url('redis://redis:6379', decode_responses=True)

        try:
            messages = await redis_client.lrange(f'room_{self.room.id}_messages_test', 0, -1)
            self.assertTrue(messages)
            last_message = json.loads(messages[-1])
            self.assertEqual(last_message['content'], message)
            self.assertEqual(last_message['user_first_name'], self.user1.first_name)
            self.assertEqual(last_message['user_last_name'], self.user1.last_name)
            self.assertEqual(last_message['user_id'], self.user1.id)
            self.assertIn('timestamp', last_message)
        finally:
            await redis_client.delete(f'room_{self.room.id}_messages')

        await communicator.disconnect()

    async def test_throttled_message_sending(self):
        communicator = await self.get_authenticated_communicator(self.user1)
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await asyncio.sleep(1)

        message1 = "Message 1"
        await communicator.send_json_to({
            'message': message1
        })

        response1 = await communicator.receive_json_from()
        self.assertEqual(response1['message'], message1)

        message2 = "Message 2"
        await communicator.send_json_to({
            'message': message2
        })

        response2 = await communicator.receive_json_from()
        self.assertIn('error', response2)

        await asyncio.sleep(1)
        await communicator.send_json_to({
            'message': message2
        })

        response3 = await communicator.receive_json_from()
        self.assertEqual(response3['message'], message2)

        await communicator.disconnect()


################### Integration TESTS #############################

class ChatAppIntegrationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.registration_url = reverse('accounts:register')
        cls.login_url = reverse('accounts:login')
        cls.user_1 = {
            'first_name': 'test',
            'last_name': 'user',
            'email': 'testuser@exampletest.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        cls.user_2 = {
            'first_name': 'test2',
            'last_name': 'user2',
            'email': 'testuser2@exampletest.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        cls.user_login_data = {
            'username': 'testuser@exampletest.com',
            'password': 'password123'
        }

    async def create_room_with_participants(self, participants):
        room = await sync_to_async(Room.objects.create)()
        await sync_to_async(room.participants.set)(participants)
        return room

    async def get_authenticated_communicator(self, user, room):
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), f"/ws/chat/{room.id}/")
        communicator.scope['user'] = user
        communicator.scope['url_route'] = {'kwargs': {'room_id': room.id}}
        return communicator

    async def test_user_registration_login_and_chat(self):
        # register a new user
        response = await sync_to_async(self.client.post)(self.registration_url, self.user_1)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(await sync_to_async(User.objects.filter(username='testuser@exampletest.com').exists)())

        # log in with the registered user
        response = await sync_to_async(self.client.post)(self.login_url, self.user_login_data)
        self.assertEqual(response.status_code, 302)

        # register 2nd user
        response = await sync_to_async(self.client.post)(self.registration_url, self.user_2)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(await sync_to_async(User.objects.filter(username='testuser2@exampletest.com').exists)())

        user1 = await sync_to_async(User.objects.get)(username='testuser@exampletest.com')
        user2 = await sync_to_async(User.objects.get)(username='testuser2@exampletest.com')

        # create a chat room with both participants
        room = await self.create_room_with_participants([user1, user2])

        # connect connect to ws channel
        communicator = await self.get_authenticated_communicator(user1, room)
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # send a message through ws
        message = "Hello world"
        await communicator.send_json_to({'message': message})

        # receive the message through ws and verify
        response = await communicator.receive_json_from()
        self.assertEqual(response['message'], message)
        self.assertEqual(response['user_first_name'], user1.first_name)
        self.assertEqual(response['user_last_name'], user1.last_name)
        self.assertEqual(response['user_id'], user1.id)

        await communicator.disconnect()
