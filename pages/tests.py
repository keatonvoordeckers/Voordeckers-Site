"""Tests for the general pages and the contact form."""

from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ContactMessage


class PageTests(TestCase):
    def test_pages_load(self):
        for name in ["home", "about", "contact"]:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_home_lists_all_eight_categories(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(len(response.context["categories"]), 8)


@override_settings(CONTACT_EMAIL="eric@example.com")
class ContactFormTests(TestCase):
    valid_data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "",
        "category": "",
        "message": "I'd like a quote for a staircase.",
    }

    def test_valid_message_is_saved_and_emailed(self):
        response = self.client.post(reverse("contact"), self.valid_data)
        self.assertRedirects(response, reverse("contact"))
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ["eric@example.com"])
        self.assertEqual(email.reply_to, ["jane@example.com"])
        self.assertIn("staircase", email.body)

    def test_success_message_shows_after_redirect(self):
        response = self.client.post(reverse("contact"), self.valid_data, follow=True)
        self.assertContains(response, "Thanks for reaching out")

    def test_invalid_email_shows_error_and_saves_nothing(self):
        data = {**self.valid_data, "email": "not-an-email"}
        response = self.client.post(reverse("contact"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "email", "Enter a valid email address.")
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_honeypot_silently_drops_bots(self):
        data = {**self.valid_data, "website": "http://spam.example"}
        response = self.client.post(reverse("contact"), data)
        self.assertRedirects(response, reverse("contact"))
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_email_failure_still_saves_message(self):
        with patch("pages.views.EmailMessage.send", side_effect=Exception("Resend is down")):
            with self.assertLogs("pages.views", level="ERROR"):
                response = self.client.post(reverse("contact"), self.valid_data)
        self.assertRedirects(response, reverse("contact"))
        self.assertEqual(ContactMessage.objects.count(), 1)