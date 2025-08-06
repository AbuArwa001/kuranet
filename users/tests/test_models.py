import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestUserModel:
    def test_user_creation(self):
        """Test basic user creation."""
        user = User.objects.create_user(
            username="newuser",
            email="newuser@example.com",
            password="strongpassword"
        )
        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.check_password("strongpassword")
        assert not user.is_staff
        assert not user.is_superuser

    def test_superuser_creation(self):
        """Test superuser creation."""
        admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword"
        )
        assert admin_user.id is not None
        assert admin_user.username == "adminuser"
        assert admin_user.email == "admin@example.com"
        assert admin_user.check_password("adminpassword")
        assert admin_user.is_staff
        assert admin_user.is_superuser

    def test_user_str_representation(self):
        """Test the string representation of a user."""
        user = User.objects.create_user(
            username="struser",
            email="str@example.com",
            password="password"
        )
        assert str(user) == "struser"

    def test_unique_email(self):
        """Test that email addresses are unique."""
        User.objects.create_user(
            username="user1",
            email="unique@example.com",
            password="password1"
        )
        with pytest.raises(Exception): # IntegrityError or ValidationError
            User.objects.create_user(
                username="user2",
                email="unique@example.com",
                password="password2"
            )

    def test_unique_username(self):
        """Test that usernames are unique."""
        User.objects.create_user(
            username="uniqueusername",
            email="user1@example.com",
            password="password1"
        )
        with pytest.raises(Exception): # IntegrityError or ValidationError
            User.objects.create_user(
                username="uniqueusername",
                email="user2@example.com",
                password="password2"
            )
