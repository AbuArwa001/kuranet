# kuranet/polls/tests/test_views.py

"""
Tests for polls views and API endpoints.

This module contains unit tests for the polls application views,
testing API functionality, authentication, and data validation.
"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from polls.models import Poll
from polls.serializers import PollSerializer
from users.models import User
from django.utils import timezone


class PollViewTests(APITestCase):
    """Test cases for Poll API views."""
    
    def setUp(self):
        """Set up test data for poll view tests."""

        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.obj = Poll.objects.create(
            title="Test Poll?",
            created_by=self.user,
            expires_at=timezone.now() + timezone.timedelta(days=1),  # required field
        )

    def test_list_view(self):
        """Test that poll list endpoint returns correct data."""
        
        url = reverse("poll-list")  # DRF router URL
        response = self.client.get(url)
        print(response.data.get("results", [])[0])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results", [])[0]["title"], "Test Poll?")
