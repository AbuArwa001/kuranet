# tests/integration_tests.py
import os
import requests
import pytest
import uuid
import time
import subprocess
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
API_PREFIX = "/api/v1/"
MAX_RETRIES = 10  # Increased retries
RETRY_DELAY = 2   # Shorter delay between retries

@pytest.fixture(scope="session", autouse=True)
def django_server():
    """Start Django server for tests"""
    server = subprocess.Popen(
        ["python", "manage.py", "runserver", "0.0.0.0:8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)  # Give server time to start
    yield
    server.terminate()
    server.wait()

@pytest.fixture
def test_user():
    return {
        "username": f"testuser_{uuid.uuid4()}",
        "email": f"test{uuid.uuid4().hex[:8]}@kuranet.com",
        "password": "TestPass123!",
    }

def test_user_registration(test_user):
    """Test user registration endpoint"""
    url = f"{BASE_URL}{API_PREFIX}auth/register/"
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                url,
                json=test_user,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            if response.status_code == 201:
                break
        except requests.exceptions.RequestException:
            if attempt == MAX_RETRIES - 1:
                pytest.fail(f"Failed to connect to server after {MAX_RETRIES} attempts")
            time.sleep(RETRY_DELAY)
    
    assert response.status_code == 201, f"Registration failed: {response.text}"