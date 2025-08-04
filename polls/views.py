from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from .models import Poll
from .serializers import PollSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response


class PollViewSet(ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
