from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .utils import log_event


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    log_event(
        user=user,
        event_type="user.login",
        description="User logged in",
        request=request
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    log_event(
        user=user,
        event_type="user.logout",
        description="User logged out",
        request=request
    )