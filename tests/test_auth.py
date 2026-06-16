"""Tests for authentication endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_user():
    """Test user registration."""
    response = client.post(
        "/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "securepassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "user_id" in data


def test_register_duplicate_email():
    """Test registering with duplicate email."""
    # Register first user
    client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "securepassword123",
            "full_name": "User One",
        },
    )

    # Try to register with same email
    response = client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "differentpassword123",
            "full_name": "User Two",
        },
    )
    assert response.status_code == 400


def test_login():
    """Test user login."""
    # Register
    client.post(
        "/auth/register",
        json={
            "email": "logintest@example.com",
            "password": "securepassword123",
            "full_name": "Login Test",
        },
    )

    # Login
    response = client.post(
        "/auth/login",
        json={
            "email": "logintest@example.com",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


def test_get_me():
    """Test getting current user profile."""
    # Register
    client.post(
        "/auth/register",
        json={
            "email": "profiletest@example.com",
            "password": "securepassword123",
            "full_name": "Profile Test",
        },
    )

    # Login and get token
    login_response = client.post(
        "/auth/login",
        json={
            "email": "profiletest@example.com",
            "password": "securepassword123",
        },
    )
    token = login_response.json()["access_token"]

    # Get profile
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "profiletest@example.com"
    assert data["full_name"] == "Profile Test"
