import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from portfolio.models import Category

from .forms import ContactForm

logger = logging.getLogger(__name__)

def home(request):
    categories = Category.objects.all()
    return render(request, "pages/home.html", {"categories": categories})

def about(request):
    return render(request, "pages/about.html")

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            if not form.cleaned_data["website"]: # Honeypot empty
                contact_message = form.save()
                notify_eric(contact_message)
            messages.success(request, "Thanks for reaching out! Eric will get back to you soon.")
            return redirect("contact")
    else:
        form = ContactForm()
    return render(request, "pages/contact.html", {"form": form})

def notify_eric(contact_message):
    """Email Eric when a new message is received. Failures are logged and the message is still saved."""
    category = contact_message.category or "Not specified"
    body = (
        f"Name: {contact_message.name}\n"
        f"Email: {contact_message.email}\n"
        f"Phone: {contact_message.phone or 'Not given'}\n"
        f"Type of work: {category}\n\n"
        f"{contact_message.message}"
    )
    email = EmailMessage(
        subject=f"New website message from {contact_message.name}",
        body=body,
        to=[settings.CONTACT_EMAIL],
        reply_to=[contact_message.email],
    )
    try:
        email.send()
    except Exception:
        logger.exception("Failed to send contact email for message %s", contact_message.pk)