from django.db.models import Q
from .models import Message


def unread_message_count(request):
    if not request.user.is_authenticated:
        return {"unread_message_count": 0}

    count = (
        Message.objects
        .filter(
            Q(conversation__visitor=request.user) |
            Q(conversation__tradesman=request.user),
            is_read=False,
        )
        .exclude(sender=request.user)
        .count()
    )

    return {"unread_message_count": count}