import pytest
from users.models import User
from rest_framework.test import APIClient
from rest_framework import status


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_test_user():
    """Fixture to create a test user."""
    user = User.objects.create_user(
        username="view_user_test",
        email="view_user@example.com",
        password="testpassword"
    )
    return user

@pytest.fixture
def create_another_user():
    """Fixture to create another test user."""
    user = User.objects.create_user(
        username="another_view_user_test",
        email="another_view_user@example.com",
        password="anotherpassword",
    )
    return user

@pytest.fixture
def create_admin_user():
    """Fixture to create an admin user."""
    user = User.objects.create_superuser(
        username="admin_view_user",
        email="admin_view@example.com",
        password="adminpassword",
    )
    user.roles.create(name='admin')
    user.save()
    return user

@pytest.fixture
def authenticated_client(api_client, create_test_user):
    """Fixture for an authenticated API client."""
    api_client.force_authenticate(user=create_test_user)
    return api_client

@pytest.fixture
def authenticated_admin_client(api_client, create_admin_user):
    """Fixture for an authenticated admin API client."""
    api_client.force_authenticate(user=create_admin_user)
    return api_client


@pytest.mark.django_db
class TestUserViewSet:
    def test_list_users_authenticated(self, authenticated_client, create_another_user):
        """Test listing users as an authenticated user."""
        response = authenticated_client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_200_OK
        # Should see at least the current user and the another user
        assert len(response.data) >= 2
            # Extract usernames from serialized data
        # users = response.data.get("results", [])
        users = response.data
        usernames = [user['username'] for user in users]

        # Check if both users are present
        assert authenticated_client.handler._force_user.username in usernames
        assert create_another_user.username in usernames
        # assert any(user.get('username') == authenticated_client.handler._force_user.username for user in response.data)
        # assert any(user.get('username') == create_another_user.username for user in response.data)

    def test_list_users_unauthenticated(self, api_client):
        """Test listing users as an unauthenticated user (should fail)."""
        response = api_client.get('/api/v1/users/')
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_retrieve_user_authenticated(self, authenticated_client, create_test_user):
        """Test retrieving own user profile as authenticated user."""
        response = authenticated_client.get(f'/api/v1/users/{create_test_user.id}/')
        # assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == create_test_user.username

    def test_retrieve_other_user_authenticated(self, authenticated_client, create_another_user):
        """Test retrieving another user's profile as authenticated user."""
        response = authenticated_client.get(f'/api/v1/users/{create_another_user.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == create_another_user.username

    def test_retrieve_user_unauthenticated(self, api_client, create_test_user):
        """Test retrieving a user profile as an unauthenticated user (should fail)."""
        response = api_client.get(f'/api/v1/users/{create_test_user.id}/')
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_update_user_self(self, authenticated_client, create_test_user):
        """Test updating own user profile."""
        updated_data = {"email": "updated_view_user@example.com"}
        response = authenticated_client.patch(f'/api/v1/users/{create_test_user.id}/', format='json', data=updated_data)
        assert response.status_code == status.HTTP_200_OK
        create_test_user.refresh_from_db()
        assert create_test_user.email == "updated_view_user@example.com"

    def test_update_user_other_user_authenticated(self, authenticated_client, create_another_user):
        """Test updating another user's profile as a non-admin authenticated user (should fail)."""
        updated_data = {"email": "hacked@example.com"}
        response = authenticated_client.patch(f'/api/v1/users/{create_another_user.id}/', format='json', data=updated_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN # Assuming IsOwnerOrAdmin or similar permission
        create_another_user.refresh_from_db()
        assert create_another_user.email != "hacked@example.com"

    def test_update_user_admin(self, authenticated_admin_client, create_test_user):
        """Test updating any user's profile as an admin user."""
        updated_data = {"email": "admin_updated@example.com"}
        response = authenticated_admin_client.patch(f'/api/v1/users/{create_test_user.id}/', format='json', data=updated_data)
        assert response.status_code == status.HTTP_200_OK
        create_test_user.refresh_from_db()
        assert create_test_user.email == "admin_updated@example.com"

    def test_delete_user_self(self, authenticated_client, create_test_user):
        """Test deleting own user account."""
        response = authenticated_client.delete(f'/api/v1/users/{create_test_user.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(id=create_test_user.id).exists()

    def test_delete_user_other_user_authenticated(self, authenticated_client, create_another_user):
        """Test deleting another user's account as a non-admin authenticated user (should fail)."""
        response = authenticated_client.delete(f'/api/v1/users/{create_another_user.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert User.objects.filter(id=create_another_user.id).exists()

    def test_delete_user_admin(self, authenticated_admin_client, create_test_user):
        """Test deleting any user's account as an admin user."""
        response = authenticated_admin_client.delete(f'/api/v1/users/{create_test_user.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(id=create_test_user.id).exists()

