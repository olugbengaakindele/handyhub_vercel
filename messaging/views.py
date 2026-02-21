from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q, Count
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from .forms import MessageSendForm
from .models import Conversation, Message, Attachment

User = get_user_model()


def _require_participant(conversation, user):
    if not conversation.is_participant(user):
        raise Http404("Conversation not found.")


@login_required
def start_conversation(request, tradesman_id):
    tradesman = get_object_or_404(User, id=tradesman_id)

    if tradesman == request.user:
        # can't message yourself
        return redirect("users:index")

    convo, _ = Conversation.objects.get_or_create(
        visitor=request.user,
        tradesman=tradesman,
    )
    return redirect("messaging:detail", conversation_id=convo.id)


@login_required
def conversation_detail(request, conversation_id):
    convo = get_object_or_404(Conversation, id=conversation_id)
    _require_participant(convo, request.user)

    convo.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)

    messages_qs = (
        convo.messages
        .select_related("sender")
        .prefetch_related("attachment")
        .order_by("created_at")
    )

    last_id = messages_qs.values_list("id", flat=True).last() or 0
    chat_messages = messages_qs[:200]

    form = MessageSendForm()

    return render(
        request,
        "messaging/conversation_detail.html",
        {"conversation": convo, "chat_messages": chat_messages, "form": form, "last_id": last_id},
    )



@login_required
@require_POST
def api_send_message(request, conversation_id):
    convo = get_object_or_404(Conversation, id=conversation_id)
    _require_participant(convo, request.user)

    form = MessageSendForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    content = (form.cleaned_data.get("content") or "").strip()
    image = form.cleaned_data.get("image")

    if not content and not image:
        return JsonResponse({"ok": False, "errors": {"content": ["Type a message or attach an image."]}}, status=400)

    now = timezone.now()

    # 1) Save message
    msg = Message.objects.create(
        conversation=convo,
        sender=request.user,
        content=content,
        created_at=now,
        is_read=False,  # recipient hasn't read it yet
    )

    # 2) Save attachment (optional)
    if image:
        Attachment.objects.create(
            message=msg,
            image=image,
            mime_type=getattr(image, "content_type", "") or "",
            size_bytes=getattr(image, "size", 0) or 0,
        )

    # 3) Bump last_message_at for inbox sorting
    Conversation.objects.filter(id=convo.id).update(last_message_at=now)

    # 4) Email notify recipient if inactive + throttled
    recipient = convo.other_party(request.user)
    if recipient and recipient.email:
        # Try to access profile last_seen_at safely
        recipient_profile = getattr(recipient, "userprofile", None) or getattr(recipient, "profile", None)
        recipient_last_seen = getattr(recipient_profile, "last_seen_at", None) if recipient_profile else None

        inactive_after = timedelta(minutes=5)     # "not active" threshold
        cooldown = timedelta(minutes=30)          # don't email more than once per 30 minutes per conversation

        is_inactive = (not recipient_last_seen) or (now - recipient_last_seen > inactive_after)

        last_email_field = convo.last_email_field_for(recipient)  # returns visitor_last_email_at / tradesman_last_email_at
        last_emailed_at = getattr(convo, last_email_field) if last_email_field else None
        within_cooldown = last_emailed_at and (now - last_emailed_at < cooldown)

        if is_inactive and not within_cooldown:
            site_url = getattr(settings, "SITE_URL", "http://127.0.0.1:8000")
            convo_link = f"{site_url}/messages/c/{convo.id}/"

            sender_name = request.user.get_full_name() or request.user.username
            recipient_name = recipient.get_full_name() or recipient.username

            subject = "You have a new message on HandymenHub"
            body = (
                f"Hi {recipient_name},\n\n"
                f"You received a new message from {sender_name}.\n\n"
                f"Open the conversation:\n{convo_link}\n\n"
                f"— HandymenHub"
            )

            send_mail(
                subject=subject,
                message=body,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[recipient.email],
                fail_silently=True,  # MVP: don't break chat if email fails
            )

            # Update the correct last-email timestamp field on the conversation
            if last_email_field:
                Conversation.objects.filter(id=convo.id).update(**{last_email_field: now})

    # 5) Return bubble HTML for sender UI
    html = render_to_string(
        "messaging/partials/message_bubble.html",
        {"m": msg, "me": request.user},
        request=request,
    )

    return JsonResponse({"ok": True, "message_id": msg.id, "html": html})



@login_required
@require_POST
def api_poll_messages(request, conversation_id):
    convo = get_object_or_404(Conversation, id=conversation_id)
    _require_participant(convo, request.user)

    form = MessageSendForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    content = (form.cleaned_data.get("content") or "").strip()
    image = form.cleaned_data.get("image")

    chat_msg = Message.objects.create(
        conversation=convo,
        sender=request.user,
        content=content,
        created_at=timezone.now(),
    )

    if image:
        Attachment.objects.create(
            message=chat_msg,
            image=image,
            mime_type=getattr(image, "content_type", "") or "",
            size_bytes=getattr(image, "size", 0) or 0,
        )

    Conversation.objects.filter(id=convo.id).update(last_message_at=timezone.now())

    html = render_to_string(
        "messaging/partials/message_bubble.html",
        {"m": chat_msg, "me": request.user},
        request=request,
    )

    return JsonResponse({"ok": True, "message_id": chat_msg.id, "html": html})


@login_required
def inbox(request):
    qs = (
        Conversation.objects
        .filter(Q(visitor=request.user) | Q(tradesman=request.user))
        .annotate(
            unread_count=Count(
                "messages",
                filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)
            )
        )
        .order_by("-last_message_at")
    )

    inbox_items = []
    for convo in qs:
        last_msg = (
            convo.messages
            .select_related("sender")
            .prefetch_related("attachment")
            .order_by("-created_at")
            .first()
        )
        inbox_items.append({"convo": convo, "last_msg": last_msg})

    return render(request, "messaging/inbox.html", {"inbox_items": inbox_items})