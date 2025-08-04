"""
Poll models for the kuranet application.

This module defines the core polling functionality including polls and their options.
"""

from django.db import models
from users.models import User
from django.utils import timezone


class Poll(models.Model):
    """
    A poll that users can vote on.
    
    Attributes:
        title: The poll question or title
        description: Optional detailed description of the poll
        created_by: User who created this poll
        created_at: Timestamp when poll was created
        expires_at: When this poll expires and voting closes
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        """Check if the poll has expired."""
        return timezone.now() > self.expires_at

    def __str__(self):
        return self.title

    # Consider adding meta classes
    # class Meta:
    #     ordering = ['-created_at']
    #     verbose_name = "Poll"
    #     verbose_name_plural = "Polls"


class Option(models.Model):
    """
    A voting option for a poll.
    
    Attributes:
        poll: The poll this option belongs to
        text: The option text that users can vote for
    """

    poll = models.ForeignKey(Poll, related_name="options", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text
