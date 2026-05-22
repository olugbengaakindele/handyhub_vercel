from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .forms import ContactMessageForm


def contact_us(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)

        if form.is_valid():
            contact_message = form.save()

            subject = f"New Contact Message from {contact_message.full_name}"

            message = f"""
                        You received a new contact message from LocalTradePros.

                        Name: {contact_message.full_name}
                        Email: {contact_message.email}

                        Message:
                        {contact_message.message}
                    """

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )

            messages.success(request, "Message sent successfully.")
            return redirect("contact:contact_us")

        messages.error(request, "Please fix the errors below and try again.")

    else:
        form = ContactMessageForm()

    return render(request, "contact/contact_us.html", {"form": form})