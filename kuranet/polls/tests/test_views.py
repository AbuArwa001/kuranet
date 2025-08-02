# kuranet/polls/tests/test_views.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from kuranet.polls.models import Poll
from kuranet.polls.serializers import PollSerializer

class PollViewTests(APITestCase):
    def setUp(self):
        self.obj = Poll.objects.create(question='Test Poll?', created_by=self.user)

    def test_list_view(self):
        url = reverse('poll-list')  # DRF router URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['question'], 'Test Poll?')
