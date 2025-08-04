from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    This serializer handles the serialization and deserialization of User instances.
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
