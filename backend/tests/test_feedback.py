"""
Tests pour le feedback utilisateur
"""
import pytest
from app.services.feedback_service import FeedbackService
from app.models.feedback import Feedback


@pytest.mark.asyncio
async def test_create_feedback():
    """Test création feedback"""
    feedback_data = {
        "user_id": "test_user",
        "response_id": "response123",
        "question": "Test question",
        "response": "Test response",
        "feedback_type": "useful",
        "rating": 5
    }
    
    result = await FeedbackService.create_feedback(feedback_data)
    assert result is not None
    assert result["feedback_type"] == "useful"


@pytest.mark.asyncio
async def test_get_stats():
    """Test récupération stats"""
    stats = await FeedbackService.get_stats()
    assert "useful" in stats
    assert "not_useful" in stats
    assert "total" in stats
