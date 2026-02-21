from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

def get_service_area_limit(user) -> int:
    profile = getattr(user, "profile", None)
    if not profile:
        return 5

    # Don't reference UserProfile constants here to avoid circular imports
    tier = getattr(profile, "tier", "free")

    limits = {
        "free": 5,
        "pro": 50,
        "premium": 50000,
    }
    return limits.get(tier, 5)


def get_gallery_photo_limit(user) -> int:
    from .models import UserProfile
    profile = getattr(user, "profile", None)
    if not profile:
        return 5

    tier = getattr(profile, "tier", "free")

    limits = {
        "free": 5,
        "pro": 50,
        "premium": 50000,
    }
    return limits.get(tier, 5)


def get_gallery_max_upload_bytes(user=None) -> int:
    return 1000 * 1024  # 500KB



def send_verification_email(request, user):
    current_site = get_current_site(request)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    subject = "Verify your email address"
    message = render_to_string("users/emails/verify_email.txt", {
        "user": user,
        "domain": current_site.domain,
        "uid": uid,
        "token": token,
        "protocol": "https" if request.is_secure() else "http",
    })

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )