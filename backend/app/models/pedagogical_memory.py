"""
Modèle pour la mémoire pédagogique utilisateur
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ErrorHistory(BaseModel):
    """Historique d'erreurs pour un concept"""
    concept: str
    error_count: int = 0
    last_error_at: Optional[datetime] = None
    error_types: List[str] = Field(default_factory=list)


class SubjectLevel(BaseModel):
    """Niveau réel par matière"""
    subject: str
    level: str = "beginner"  # beginner, intermediate, advanced
    confidence_score: float = 0.0  # 0.0 à 1.0
    last_assessed_at: Optional[datetime] = None
    total_time_spent: int = 0  # en minutes
    modules_completed: int = 0


class LearningStyle(BaseModel):
    """Style d'apprentissage préféré"""
    preferred_format: str = "balanced"  # visual, step_by_step, summary, balanced
    detail_level: str = "medium"  # low, medium, high
    examples_preference: bool = True
    visual_aids_preference: bool = True


class PedagogicalMemory(BaseModel):
    """Mémoire pédagogique complète d'un utilisateur"""
    user_id: str
    subject_levels: Dict[str, SubjectLevel] = Field(default_factory=dict)
    error_history: List[ErrorHistory] = Field(default_factory=list)
    learning_style: LearningStyle = Field(default_factory=LearningStyle)
    preferred_explanation_length: str = "medium"  # short, medium, long
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "subject_levels": {
                    "mathematics": {
                        "subject": "mathematics",
                        "level": "intermediate",
                        "confidence_score": 0.75,
                        "last_assessed_at": "2026-01-15T10:00:00Z",
                        "total_time_spent": 120,
                        "modules_completed": 5
                    }
                },
                "error_history": [
                    {
                        "concept": "dérivées",
                        "error_count": 3,
                        "last_error_at": "2026-01-15T09:00:00Z",
                        "error_types": ["calcul", "application"]
                    }
                ],
                "learning_style": {
                    "preferred_format": "step_by_step",
                    "detail_level": "high",
                    "examples_preference": True,
                    "visual_aids_preference": True
                },
                "preferred_explanation_length": "medium"
            }
        }
