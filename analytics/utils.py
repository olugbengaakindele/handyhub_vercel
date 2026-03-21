def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def log_event(
    *,
    user=None,
    event_type,
    instance=None,
    description="",
    old_data=None,
    new_data=None,
    metadata=None,
    request=None,
):
    from .models import EventLog

    EventLog.objects.create(
        user=user,
        event_type=event_type,

        app_label=instance._meta.app_label if instance else None,
        model_name=instance._meta.model_name if instance else None,
        object_id=str(instance.pk) if instance else None,

        description=description,

        old_data=old_data,
        new_data=new_data,
        metadata=metadata,

        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get("HTTP_USER_AGENT") if request else None,
    )