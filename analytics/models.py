from django.conf import settings
from django.db import models


class EventLog(models.Model):

    EVENT_TYPES = [
        ("user.signup", "User Signup"),
        ("user.login", "User Login"),
        ("user.logout", "User Logout"),

        ("profile.updated", "Profile Updated"),

        ("service.added", "Service Added"),
        ("service.updated", "Service Updated"),
        ("service.deleted", "Service Deleted"),

        ("service_area.added", "Service Area Added"),
        ("service_area.deleted", "Service Area Deleted"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_logs"
    )

    event_type = models.CharField(
        max_length=100,
        db_index=True,
        choices=EVENT_TYPES
    )

    # what object was affected
    app_label = models.CharField(max_length=100, null=True, blank=True)
    model_name = models.CharField(max_length=100, null=True, blank=True)
    object_id = models.CharField(max_length=100, null=True, blank=True)

    description = models.TextField(blank=True, null=True)

    old_data = models.JSONField(blank=True, null=True)
    new_data = models.JSONField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)

    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type} - {self.user} - {self.created_at}"