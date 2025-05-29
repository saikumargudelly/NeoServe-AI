"""
Configuration and fixtures for pytest.
"""
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from neoserve_ai.main import app
from neoserve_ai.config.settings import init_config

# Initialize test configuration
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment."""
    # Set test environment variables
    os.environ["ENVIRONMENT"] = "test"
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"
    
    # Initialize configuration
    init_config()

# Test client fixture
@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client

# Fixture to clear the test database between tests
@pytest.fixture(autouse=True)
def clear_test_database():
    """Clear the test database between tests."""
    # This is a placeholder. In a real application, you would clear the test database here.
    yield
    # Cleanup after test

# Fixture for test user data
@pytest.fixture
def test_user_data():
    """Provide test user data."""
    return {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
    }

# Fixture for authenticated test client
@pytest.fixture
def authenticated_client(client, test_user_data):
    """Create an authenticated test client."""
    # Register test user
    response = client.post(
        "/api/v1/auth/register",
        json=test_user_data,
    )
    assert response.status_code == 201
    
    # Login to get token
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Set auth header
    client.headers = {"Authorization": f"Bearer {token}"}
    return client
