import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from django.contrib.auth import get_user_model

from .models import Message, Chat, Contact
from .views import get_last_10_messages


User = get_user_model()


class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None
        self.room_group_name = None

    def fetch_messages(self, data):
        """
        Fetch messages from db
        :param data:
        :return:
        """
        messages = get_last_10_messages(data['chatId'])
        self.send_message({
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        })

    def new_message(self, data):
        """
        Create new message in the DB and send it to chat
        :param data:
        :return:
        """
        author_user = User.objects.filter(username=data['from'])[0]
        message = Message.objects.create(author=author_user, content=data['message'])

        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))

        return result

    def message_to_json(self, message):
        return {
            'id': message.id,
            'author': message.contact.user .username,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        # TODO: investigate if we need this
        if not text_data:
            raise Exception('Text data is None. WebSocket Consumer can\'t continue consuming process')

        data = json.loads(text_data)

        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        self.send(text_data=json.dumps(event['message']))
