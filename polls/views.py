"""
Views for the polls application.

This module contains API views for managing polls, including CRUD operations
and custom business logic for poll creation.
"""

# Remove these unused imports:
# from rest_framework import generics      # Not used
# from django.utils import timezone       # Not used  
# from django.http import JsonResponse     # Not used
# from rest_framework.decorators import api_view  # Not used
# from rest_framework.response import Response    # Not used

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
    """
    ViewSet for managing polls.
    
    Provides CRUD operations for polls with the following permissions:
    - Anonymous users: Read-only access
    - Authenticated users: Full CRUD access
    
    The creating user is automatically set as the poll owner.
    """

    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """
        Save the poll with the requesting user as the creator.
        
        Args:
            serializer: The validated poll serializer
        """

        serializer.save(created_by=self.request.user)
