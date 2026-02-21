from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactMessageForm

def contact_us(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Message sent successfully.")
            return redirect("users:index")
        else:
            print(form.errors)  # 👈 add this
            messages.error(request, "Please fix the errors below and try again.")
    else:
        form = ContactMessageForm()

    return render(request, "contact/contact_us.html", {"form": form})
