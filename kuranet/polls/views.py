from rest_framework import generics
from .models import Poll
from .serializers import PollSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class PollCreateView(generics.CreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class PollListView(generics.ListAPIView):
    serializer_class = PollSerializer

    def get_queryset(self):
        return Poll.objects.filter(expires_at__gt=timezone.now()).order_by('-created_at')

class PollDetailView(generics.RetrieveAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
