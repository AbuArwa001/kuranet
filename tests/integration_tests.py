import os
import requests
import pytest
import uuid
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
API_PREFIX = "/api/v1/"

@pytest.fixture
def test_user():
    return {
        "username": f"testuser_{uuid.uuid4()}",
        "email": f"test{uuid.uuid4().hex[:8]}@kuranet.com",
        "password": "TestPass123!",
    }

def test_user_registration(test_user):
    """Test user registration endpoint"""
    # Test successful registration
    url = f"{BASE_URL}{API_PREFIX}auth/register/"
    response = requests.post(url, json=test_user)
    assert response.status_code == 201
    
    # Test duplicate registration
    dup_response = requests.post(url, json=test_user)
    assert dup_response.status_code == 400
    
    # Test login with new user
    login_url = f"{BASE_URL}{API_PREFIX}auth/login/"
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    login_response = requests.post(login_url, json=login_data)
    assert login_response.status_code == 200
    assert "access" in login_response.json()
    assert "refresh" in login_response.json()
    
    # Test invalid login
    bad_login = requests.post(login_url, json={
        "username": test_user["username"],
        "password": "wrongpassword"
    })
    assert bad_login.status_code == 401

def test_protected_endpoints(test_user):
    """Test endpoints requiring authentication"""
    # First register and login to get a valid token
    register_url = f"{BASE_URL}{API_PREFIX}auth/register/"
    requests.post(register_url, json=test_user)
    
    login_url = f"{BASE_URL}{API_PREFIX}auth/login/"
    auth_response = requests.post(login_url, json={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    
    # Verify we got tokens
    assert "access" in auth_response.json()
    token = auth_response.json()["access"]
    
    # Test protected endpoint - replace with your actual endpoint
    protected_url = f"{BASE_URL}{API_PREFIX}users/"  # Example endpoint
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with valid token
    protected_response = requests.get(protected_url, headers=headers)
    assert protected_response.status_code == 200
    
    # Test without token
    no_auth_response = requests.get(protected_url)
    assert no_auth_response.status_code in [401, 403]
def test_invalid_registration():
    """Test registration with invalid data"""
    url = f"{BASE_URL}{API_PREFIX}auth/register/"
    
    # Missing required field
    response = requests.post(url, json={
        "username": "testuser",
        "password": "testpass" 
        # Missing email
    })
    assert response.status_code == 400
    
    # Invalid email format
    response = requests.post(url, json={
        "username": "testuser",
        "email": "not-an-email",
        "password": "testpass"
    })
    assert response.status_code == 400

def test_refresh_token(test_user):
    """Test token refresh flow"""
    # Register and login
    register_url = f"{BASE_URL}{API_PREFIX}auth/register/"
    requests.post(register_url, json=test_user)
    
    login_url = f"{BASE_URL}{API_PREFIX}auth/login/"
    auth_response = requests.post(login_url, json={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    refresh_token = auth_response.json()["refresh"]
    
    # Test refresh
    refresh_url = f"{BASE_URL}{API_PREFIX}auth/refresh/"
    refresh_response = requests.post(refresh_url, json={
        "refresh": refresh_token
    })
    assert refresh_response.status_code == 200
    assert "access" in refresh_response.json()