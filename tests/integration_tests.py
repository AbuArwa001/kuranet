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

def test_protected_endpoints():
    """Test endpoints requiring authentication"""
    # First get a valid token
    auth_url = f"{BASE_URL}{API_PREFIX}auth/login/"
    auth_response = requests.post(auth_url, json={
        "username": "testuser",
        "password": "testpass"
    })
    token = auth_response.json()["access"]
    
    # Test protected endpoint
    protected_url = f"{BASE_URL}{API_PREFIX}users/"
    headers = {"Authorization": f"Bearer {token}"}
    protected_response = requests.get(protected_url, headers=headers)
    assert protected_response.status_code == 200
    
    # Test without token
    no_auth_response = requests.get(protected_url)
    assert no_auth_response.status_code == 403