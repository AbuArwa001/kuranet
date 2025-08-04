"""
User authentication and management views.

This module provides API endpoints for user registration, authentication,
and user management using Django REST Framework ViewSets.
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user accounts.
    
    Provides CRUD operations for users. All endpoints require authentication.
    Only authenticated users can access user data.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet for authentication operations.
    
    Handles user registration and logout. All endpoints are publicly accessible
    since users need to register and authenticate without existing credentials.
    """

    permission_classes = [AllowAny]

    # @action(detail=False, methods=['post'])
    # def register(self, request):
    #     serializer = UserSerializer(data=request.data)
    #     if serializer.is_valid():
    #         user = serializer.save()
    #         return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        """
        Register a new user account.
        
        Creates a new user with the provided data and returns the user
        information along with JWT access and refresh tokens.
        
        Args:
            request: HTTP request with user registration data
            
        Returns:
            Response: User data with JWT tokens (201) or validation errors (400)
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def logout(self, request):
                """
        Log out the current user.
        
        Note: JWT tokens are stateless, so this endpoint provides a client-side
        logout confirmation. Actual token invalidation should be handled by
        the client (removing tokens from storage).
        
        Args:
            request: HTTP request
            
        Returns:
            Response: Success message (200)
        """
        
        # Optional: JWT doesn't manage logout server-side.
        return Response({"message": "Logged out."}, status=status.HTTP_200_OK)
