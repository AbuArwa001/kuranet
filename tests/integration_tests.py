"""
Integration tests for Kuranet Django application
These tests verify interactions between components and external services
"""

import os
import requests
import pytest
import unittest
from dotenv import load_dotenv
import uuid
import time
import json

# Load environment variables from .env file
load_dotenv()

# Configuration
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")  # Configurable base URL
API_PREFIX = "/api/v1/"
MAX_RETRIES = 5
RETRY_DELAY = 3  # seconds

# Test user credentials
def generate_test_user():
    return {
        "username": f"testuser_{uuid.uuid4()}",
        "email": f"test{uuid.uuid4().hex[:8]}@kuranet.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "TestPass123!",
    }

class IntegrationTest(unittest.TestCase):
    """Base class for integration tests"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.server_url = f"{BASE_URL}{API_PREFIX}"
        cls.wait_for_server()

    @classmethod
    def wait_for_server(cls, max_retries=MAX_RETRIES, delay=RETRY_DELAY):
        """Wait for server to become available"""
        for i in range(max_retries):
            try:
                response = requests.get(cls.server_url, timeout=5)
                if response.status_code == 200:
                    return
            except requests.exceptions.RequestException:
                pass
            if i < max_retries - 1:
                time.sleep(delay)
        pytest.fail(f"Server not available at {cls.server_url} after {max_retries} attempts")

    def test_user_registration(self):
        """Test user registration endpoint"""
        url = f"{self.server_url}auth/register/"
        test_user = generate_test_user()
        
        try:
            response = requests.post(
                url,
                json=test_user,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Debug output
            print(f"Registration Response: {response.status_code} - {response.text}")
            
            if response.status_code != 201:
                # Try to get error details
                try:
                    error_details = response.json()
                    print(f"Error details: {error_details}")
                except ValueError:
                    pass
            
            self.assertEqual(response.status_code, 201, 
                           f"User registration failed. Response: {response.text}")
            
            # Verify user was actually created
            if response.status_code == 201:
                login_url = f"{self.server_url}auth/login/"
                login_response = requests.post(
                    login_url,
                    json={
                        "username": test_user["username"],
                        "password": test_user["password"]
                    },
                    timeout=10
                )
                self.assertEqual(login_response.status_code, 200,
                                "Registered user cannot login")

        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {str(e)}")


if __name__ == "__main__":
    # Configure pytest to run unittest-style tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    # Alternatively, run with pytest directly
    # pytest.main(["-v", "--tb=native", __file__])