# kuranet/polls/tests/test_views.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from polls.models import Poll
from polls.serializers import PollSerializer
from users.models import User
from django.utils import timezone


class PollViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass", email="testuser@example.com")
        self.obj = Poll.objects.create(
            title="Test Poll?",
            user=self.user,
            closes_at=timezone.now() + timezone.timedelta(days=1),
        )

    def test_list_view(self):
        url = reverse("poll-list") 
        response = self.client.get(url)
        # print(response.data.get("results", [])[0])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results", [])[0]["title"], "Test Poll?")
