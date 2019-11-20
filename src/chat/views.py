from django.shortcuts import get_object_or_404

from .models import Chat


def get_last_10_messages(chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    return reversed(chat.messages.order_by('-timestamp').all()[:10])
