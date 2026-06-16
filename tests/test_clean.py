"""Tests for text cleaning endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_token():
    """Create a test user and return auth token."""
    client.post(
        "/auth/register",
        json={
            "email": "cleantest@example.com",
            "password": "securepassword123",
            "full_name": "Clean Test",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "cleantest@example.com",
            "password": "securepassword123",
        },
    )
    return response.json()["access_token"]


def test_clean_text_with_grammar(auth_token):
    """Test cleaning text with grammar operation."""
    response = client.post(
        "/clean/text",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "text": "ur text has grammar mistakes",
            "operations": ["grammar"],
            "target_style": "formal",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "cleaned_text" in data
    assert data["operations_applied"] == ["grammar"]


def test_clean_text_with_spaces(auth_token):
    """Test cleaning extra spaces."""
    response = client.post(
        "/clean/text",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "text": "text   with    extra    spaces",
            "operations": ["spaces"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "extra" in data["cleaned_text"]
    # Should have fewer spaces
    assert data["cleaned_text"].count("  ") == 0


def test_clean_text_with_emojis(auth_token):
    """Test removing emojis."""
    response = client.post(
        "/clean/text",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "text": "Hello 👋 world 🌍 !",
            "operations": ["emojis"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "👋" not in data["cleaned_text"]
    assert "🌍" not in data["cleaned_text"]


def test_clean_text_with_pii(auth_token):
    """Test PII removal."""
    response = client.post(
        "/clean/text",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "text": "My email is john@example.com and phone is 555-1234567",
            "operations": ["pii"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    # Should have redacted PII
    assert "john@example.com" not in data["cleaned_text"] or "[REDACTED]" in data[
        "cleaned_text"
    ]


def test_autocorrect(auth_token):
    """Test autocorrect endpoint."""
    response = client.post(
        "/clean/autocorrect",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "text": "ur text has   grammar mistakess!!!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["operations_applied"]) > 0


def test_batch_clean(auth_token):
    """Test batch cleaning."""
    response = client.post(
        "/clean/batch",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "texts": [
                "text 1 with errors!!!",
                "text 2 needs   cleaning",
                "text 3 😂",
            ],
            "operations": ["spaces", "grammar", "emojis"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_processed"] == 3
    assert len(data["results"]) == 3


def test_clean_text_unauthorized():
    """Test cleaning without authentication."""
    response = client.post(
        "/clean/text",
        json={
            "text": "some text",
            "operations": ["grammar"],
        },
    )
    assert response.status_code == 401


def test_clean_text_exceeds_max_length(auth_token):
    """Test text exceeding plan limit."""
    # Create very long text (more than free plan allows)
    long_text = "a" * 100000  # 100KB text

    response = client.post(
        "/clean/text",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "text": long_text,
            "operations": ["grammar"],
        },
    )
    # Should return 413 or 403 (depends on plan)
    assert response.status_code in [403, 413]
