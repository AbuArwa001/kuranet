from rest_framework import serializers
from .models import Poll, Option


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "text"]


class PollSerializer(serializers.ModelSerializer):
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
        from django.utils import timezone

        if value <= timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future.")
        return value

    def create(self, validated_data):
        options_data = validated_data.pop("options")
        poll = Poll.objects.create(**validated_data)
        for option_data in options_data:
            Option.objects.create(poll=poll, **option_data)
        return poll
