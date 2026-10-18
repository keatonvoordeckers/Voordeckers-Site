"""Forms for the sites pages"""

from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """Contact form with a hidden honeypot field to catch spam bots."""

    # Honeypot: hidden from people by CSS, but bots fill in every field.
    website = forms.CharField(required=False, label="Leave this field empty")


    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "category", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 6})
        }
        labels = {
            "phone": "Phone (optional)"
        }