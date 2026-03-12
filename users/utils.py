from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone
from django.db.models import F

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



def increment_profile_metric(profile, field_name):
    from .models import ProfileDailyAnalytics  # import here to avoid circular import
    valid_fields = {
        "profile_views",
        "message_clicks",
        "phone_clicks",
        "email_clicks",
        "website_clicks",
        "gallery_opens",
        "license_document_views",
    }

    if field_name not in valid_fields:
        return

    today = timezone.localdate()

    obj, created = ProfileDailyAnalytics.objects.get_or_create(
        profile=profile,
        date=today,
        defaults={field_name: 1},
    )

    if not created:
        ProfileDailyAnalytics.objects.filter(pk=obj.pk).update(
            **{field_name: F(field_name) + 1}
        )