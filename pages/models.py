"""Models for site's pages"""

from django.db import models

from portfolio.models import Category


class ContactMessage(models.Model):
    """A message sent through the contact form within the website."""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL, # deleting a category keeps its messages
        null=True,
        blank=True,
        related_name="messages",
        verbose_name="type of work"
    )
    message = models.TextField()
    is_handled = models.BooleanField(default=False) # admin checks this off once replied
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ["-created_at"] # newest first


    # Method to return the string representation of a ContactMessage, ex: Bob (2026-10-17)
    def __str__(self):
        return f"{self.name} ({self.created_at:%Y-%m-%d})"

    
    
