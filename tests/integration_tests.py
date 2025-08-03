"""
Integration tests for Kuranet Django application
"""
import os
import requests
import pytest
import uuid
import time
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
API_PREFIX = "/api/v1/"
MAX_RETRIES = 5
RETRY_DELAY = 3

@pytest.fixture
def test_user():
    return {
        "username": f"testuser_{uuid.uuid4()}",
        "email": f"test{uuid.uuid4().hex[:8]}@kuranet.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "TestPass123!",
    }

def wait_for_server():
    """Wait for server to become available"""
    server_url = f"{BASE_URL}{API_PREFIX}"
    for i in range(MAX_RETRIES):
        try:
            response = requests.get(server_url, timeout=5)
            if response.status_code == 200:
                return server_url
        except requests.exceptions.RequestException:
            pass
        if i < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY)
    pytest.fail(f"Server not available at {server_url} after {MAX_RETRIES} attempts")

def test_user_registration(test_user):
    """Test user registration endpoint"""
    server_url = wait_for_server()
    url = f"{server_url}auth/register/"
    
    response = requests.post(
        url,
        json=test_user,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    # Debug output
    print(f"Registration Response: {response.status_code} - {response.text}")
    
    assert response.status_code == 201, f"User registration failed. Response: {response.text}"
    
    # Verify login works
    if response.status_code == 201:
        login_url = f"{server_url}auth/login/"
        login_response = requests.post(
            login_url,
            json={
                "username": test_user["username"],
                "password": test_user["password"]
            },
            timeout=10
        )
        assert login_response.status_code == 200, "Registered user cannot login"