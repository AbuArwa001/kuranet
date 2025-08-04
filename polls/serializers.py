"""
Serializers for the polls application.

This module handles API serialization/deserialization for Poll and Option models,
including validation and nested object creation.
"""

from rest_framework import serializers
from .models import Poll, Option


class OptionSerializer(serializers.ModelSerializer):
    """Serializer for poll options."""

    class Meta:
        model = Option
        fields = ["id", "text"]


class PollSerializer(serializers.ModelSerializer):
    """
    Serializer for polls with nested options.
    
    Handles creation of polls with their associated options in a single request.
    The created_by field is automatically set to the requesting user's username.
    """

    options = OptionSerializer(many=True)
    created_by = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = Poll
        fields = [
            "id",
            "title",
            "description",
            "created_by",
            "created_at",
            "expires_at",
            "options",
        ]

    def validate_expires_at(self, value):
        """
        Validate that the expiration date is in the future.
        
        Args:
            value: The expires_at datetime value
            
        Returns:
            datetime: The validated expiration date
            
        Raises:
            ValidationError: If expiration date is not in the future
        """

        from django.utils import timezone

        if value <= timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future.")
        return value

    def create(self, validated_data):
        """
        Create a poll with its associated options.
        
        Args:
            validated_data: Validated data including nested options
            
        Returns:
            Poll: The created poll instance with options
        """
        
        options_data = validated_data.pop("options")
        poll = Poll.objects.create(**validated_data)
        for option_data in options_data:
            Option.objects.create(poll=poll, **option_data)
        return poll
