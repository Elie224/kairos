"""
Modèle pour le feedback utilisateur sur les réponses IA
"""
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class Feedback(BaseModel):
    """Feedback utilisateur sur une réponse IA"""
    user_id: str
    response_id: str  # ID de la réponse IA (peut être un hash)
    question: str
    response: str
    feedback_type: str = "useful"  # useful, not_useful
    rating: Optional[int] = None  # 1-5 (optionnel)
    comment: Optional[str] = None
    model_used: Optional[str] = None
    subject: Optional[str] = None
    module_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "response_id": "response456",
                "question": "Qu'est-ce qu'une dérivée?",
                "response": "Une dérivée est...",
                "feedback_type": "useful",
                "rating": 5,
                "comment": "Très claire explication",
                "model_used": "gpt-5-mini",
                "subject": "mathematics",
                "module_id": "module789"
            }
        }
