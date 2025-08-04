"""
User serializers for authentication and user management.

This module handles user registration, serialization, and JWT token generation
for the kuranet application's authentication system.
"""

from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with JWT token generation.
    
    Handles user registration and automatically generates JWT tokens
    upon successful user creation. The password field is write-only
    for security.
    
    Returns:
        dict: User data with access and refresh JWT tokens
    """

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "password"]
        read_only_fields = ["id"]  # id field is read-only
        extra_kwargs = {
            "password": {
                "write_only": True
            }  # Password should not be returned in responses
        }

    def create(self, validated_data):
        # TODO: Remove debug prints before production
        """
        Create a new user with the provided data.
        
        Args:
            validated_data (dict): Validated user data from request
            
        Returns:
            User: The created user instance
        """
        print("Creating user with data test:", validated_data)
        data = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            password=validated_data["password"],
        )
        print("User created:", data)
        return data

    def to_representation(self, instance):
        """
        Convert user instance to API response with JWT tokens.
        
        Args:
            instance (User): User instance to serialize
            
        Returns:
            dict: User data with access and refresh tokens
        """
        
        refresh = RefreshToken.for_user(instance)
        return {
            "user": {
                "id": instance.id,
                "username": instance.username,
                "email": instance.email,
                "first_name": instance.first_name,
                "last_name": instance.last_name,
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
