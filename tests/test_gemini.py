"""
Unit Tests: Gemini Service Layer
--------------------------------
Tests API key validation, empty input handling, mocked generation responses,
and graceful exception handling without making live network requests.
"""

import pytest
from unittest.mock import MagicMock, patch
from services.gemini_service import GeminiService


def test_missing_api_key_returns_friendly_message():
    """Verifies that an unconfigured service returns a gentle message without crashing."""
    service = GeminiService(api_key="")
    assert not service.is_configured()
    
    response = service.generate_response("What causes cramps?")
    assert "not yet configured" in response or "GEMINI_API_KEY" in response
    # Ensure no raw stack traces or internal secrets are returned
    assert "Traceback" not in response
    assert "Exception" not in response


def test_empty_user_input():
    """Verifies that empty queries are rejected with guidance."""
    service = GeminiService(api_key="fake-key-for-test")
    
    assert "Please enter a question" in service.generate_response("")
    assert "Please enter a question" in service.generate_response("   ")


@patch("services.gemini_service.genai.Client")
def test_successful_response_handling(mock_client_cls):
    """Verifies response extraction from a successful mocked API call."""
    mock_instance = MagicMock()
    mock_client_cls.return_value = mock_instance
    
    # Mock return value of client.models.generate_content
    mock_response = MagicMock()
    mock_response.text = "Menstrual cramps are caused by uterine muscle contractions prompted by prostaglandins."
    mock_instance.models.generate_content.return_value = mock_response

    service = GeminiService(api_key="test-valid-key")
    result = service.generate_response("What causes cramps?")
    
    assert "prostaglandins" in result
    mock_instance.models.generate_content.assert_called_once()


@patch("services.gemini_service.genai.Client")
def test_api_failure_recovers_gracefully(mock_client_cls):
    """Verifies that an unexpected API failure returns a calm user message without crashing."""
    mock_instance = MagicMock()
    mock_client_cls.return_value = mock_instance
    
    # Simulate an API connection timeout or quota error
    mock_instance.models.generate_content.side_effect = RuntimeError("Google GenAI 503 Service Unavailable")

    service = GeminiService(api_key="test-valid-key")
    result = service.generate_response("Tell me about PCOS")
    
    # User should see a friendly fallback, NOT the raw exception
    assert "having trouble connecting" in result.lower()
    assert "503" not in result
    assert "RuntimeError" not in result
    assert "Traceback" not in result
