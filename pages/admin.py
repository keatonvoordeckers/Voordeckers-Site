"""Define how the pages app's models appear in the admin."""

from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "category", "created_at", "is_handled"]
    list_editable = ["is_handled"]
    list_filter = ["is_handled", "category"]
    search_fields = ["name", "email", "message"]
    readonly_fields = ["name", "email", "phone", "category", "message", "created_at"]
