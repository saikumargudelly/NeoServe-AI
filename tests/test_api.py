"""
Tests for the NeoServe AI API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from neoserve_ai.main import app
from neoserve_ai.schemas.user import UserCreate, User, Token
from neoserve_ai.utils.auth import get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import datetime, timedelta

# Test client
client = TestClient(app)

# Test data
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_USER_FIRST_NAME = "Test"
TEST_USER_LAST_NAME = "User"

# Fixture for test user data
@pytest.fixture
def test_user():
    return {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "first_name": TEST_USER_FIRST_NAME,
        "last_name": TEST_USER_LAST_NAME,
    }

# Fixture for test client with auth headers
@pytest.fixture
def authenticated_client(test_user):
    # Register test user
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user["email"],
            "password": test_user["password"],
            "first_name": test_user["first_name"],
            "last_name": test_user["last_name"],
        },
    )
    assert response.status_code == 201
    
    # Get access token
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": test_user["email"],
            "password": test_user["password"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Set auth header
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_user(test_user):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "email" in data
    assert data["email"] == "newuser@example.com"
    assert "password" not in data  # Password should not be in response

def test_login(test_user):
    """Test user login."""
    # First register the test user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user["email"],
            "password": test_user["password"],
            "first_name": test_user["first_name"],
            "last_name": test_user["last_name"],
        },
    )
    
    # Test login
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": test_user["email"],
            "password": test_user["password"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_current_user(authenticated_client):
    """Test getting the current user's profile."""
    response = authenticated_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert data["email"] == TEST_USER_EMAIL

def test_chat_endpoint(authenticated_client):
    """Test the chat endpoint."""
    response = authenticated_client.post(
        "/api/v1/chat",
        json={
            "message": "Hello, how are you?",
            "session_id": "test-session-123",
            "message_id": "msg-123",
            "metadata": {"test": "data"}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "intent" in data
    assert "confidence" in data

def test_chat_history(authenticated_client):
    """Test getting chat history."""
    # First send a message to create a session
    authenticated_client.post(
        "/api/v1/chat",
        json={
            "message": "Hello, how are you?",
            "session_id": "test-session-123",
            "message_id": "msg-123"
        }
    )
    
    # Get chat history
    response = authenticated_client.get("/api/v1/chat/history/test-session-123")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_escalate_conversation(authenticated_client):
    """Test escalating a conversation to a human agent."""
    response = authenticated_client.post(
        "/api/v1/chat/escalate",
        json={
            "session_id": "test-session-123",
            "reason": "Need human assistance",
            "message": "I need to speak with a human"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"
    assert "escalation_id" in data
