import pytest
from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.serializers import UserSerializer, RegisterSerializer # Assuming RegisterSerializer exists

User = get_user_model()

@pytest.mark.django_db
class TestUserSerializer:
    def test_user_serialization(self):
        """Test UserSerializer serialization."""
        user = User.objects.create_user(
            username="serialize_user",
            email="serialize@example.com",
            password="testpassword"
        )
        serializer = UserSerializer(user)
        data = serializer.data
        assert data['id'] == user.id
        assert data['username'] == user.username
        assert data['email'] == user.email
        assert 'password' not in data # Passwords should not be serialized

    def test_user_deserialization_read_only(self):
        """Test that UserSerializer is read-only for most fields."""
        data = {
            'username': 'new_username',
            'email': 'new_email@example.com',
            'password': 'new_password'
        }
        serializer = UserSerializer(data=data)
        # UserSerializer is typically used for displaying user info, not creating/updating directly
        # Unless it's a partial update for specific fields.
        # If it's read-only, it won't be valid for creation.
        assert not serializer.is_valid() # Should fail as it's read-only for creation
        assert 'username' in serializer.errors or 'email' in serializer.errors # Depending on fields

@pytest.mark.django_db
class TestRegisterSerializer:
    def test_register_serialization(self):
        """Test RegisterSerializer serialization (should be empty)."""
        # RegisterSerializer is typically for deserialization (creating a user)
        # It doesn't serialize an existing user.
        serializer = RegisterSerializer()
        assert not serializer.data # Should be empty or raise error if called without instance

    def test_register_deserialization_valid(self):
        """Test RegisterSerializer deserialization with valid data."""
        data = {
            'username': 'register_test_user',
            'email': 'register@example.com',
            'password': 'StrongPassword123!',
            'password2': 'StrongPassword123!'
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid(raise_exception=True)
        user = serializer.save()
        assert user.id is not None
        assert user.username == 'register_test_user'
        assert user.email == 'register@example.com'
        assert user.check_password('StrongPassword123!')

    def test_register_deserialization_invalid_passwords_mismatch(self):
        """Test RegisterSerializer with mismatched passwords."""
        data = {
            'username': 'mismatch_user',
            'email': 'mismatch@example.com',
            'password': 'Password1',
            'password2': 'Password2'
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors # Assuming custom validation for password match

    def test_register_deserialization_invalid_missing_fields(self):
        """Test RegisterSerializer with missing required fields."""
        data = {
            'username': 'incomplete_user',
            'password': 'Password123!',
            'password2': 'Password123!'
            # Missing email
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_register_deserialization_invalid_duplicate_username(self):
        """Test RegisterSerializer with duplicate username."""
        User.objects.create_user(
            username="existing_user",
            email="existing@example.com",
            password="password"
        )
        data = {
            'username': 'existing_user',
            'email': 'new_email@example.com',
            'password': 'NewPassword123!',
            'password2': 'NewPassword123!'
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'username' in serializer.errors # Assuming unique validation
