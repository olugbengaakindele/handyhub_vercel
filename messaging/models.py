import uuid
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


User = settings.AUTH_USER_MODEL


def chat_upload_path(instance, filename):
    # uploads/chat/<conversation_id>/<uuid>_<filename>
    return f"chat/{instance.message.conversation.id}/{uuid.uuid4()}_{filename}"


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # visitor = the person who initiated
    visitor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="conversations_started",
    )
    tradesman = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="conversations_received",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # Updated automatically whenever the conversation changes (e.g., new message)
    last_message_at = models.DateTimeField(auto_now=True)

    # ✅ NEW: email throttle timestamps (to avoid spamming)
    visitor_last_email_at = models.DateTimeField(null=True, blank=True)
    tradesman_last_email_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["visitor", "tradesman"],
                name="unique_conversation_pair",
            )
        ]
        indexes = [
            models.Index(fields=["visitor", "last_message_at"]),
            models.Index(fields=["tradesman", "last_message_at"]),
        ]

    def participants_q(self, user):
        return Q(visitor=user) | Q(tradesman=user)

    def is_participant(self, user):
        return user == self.visitor or user == self.tradesman

    def other_party(self, user):
        """Returns the other user in the conversation (handy for UI + notifications)."""
        if user == self.visitor:
            return self.tradesman
        if user == self.tradesman:
            return self.visitor
        return None

    def last_email_field_for(self, user):
        """Which last-email field belongs to this user."""
        if user == self.visitor:
            return "visitor_last_email_at"
        if user == self.tradesman:
            return "tradesman_last_email_at"
        return None

class Message(models.Model):
    id = models.BigAutoField(primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_sent")
    content = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # simple read marker (MVP)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    @property
    def has_attachment(self):
        return hasattr(self, "attachment")


class Attachment(models.Model):
    message = models.OneToOneField(Message, on_delete=models.CASCADE, related_name="attachment")
    image = models.ImageField(upload_to=chat_upload_path)

    mime_type = models.CharField(max_length=100, blank=True)
    size_bytes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)



