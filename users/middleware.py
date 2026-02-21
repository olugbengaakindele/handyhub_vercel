from django.utils import timezone

class UpdateLastSeenMiddleware:
    """
    Updates request.user.profile.last_seen_at for authenticated users.
    Lightweight and good enough for MVP.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            # Avoid crashing if profile isn't created yet
            profile = getattr(user, "userprofile", None) or getattr(user, "profile", None)
            if profile:
                now = timezone.now()
                # Only update if at least 60 seconds passed (reduces DB writes)
                if not profile.last_seen_at or (now - profile.last_seen_at).total_seconds() >= 60:
                    profile.last_seen_at = now
                    profile.save(update_fields=["last_seen_at"])

        return response
