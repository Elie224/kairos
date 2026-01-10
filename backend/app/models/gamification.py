"""
Modèles pour la gamification avancée
"""
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from app.models import Subject, Difficulty


class QuestType(str, Enum):
    """Type de quête"""
    DAILY = "daily"
    WEEKLY = "weekly"
    ACHIEVEMENT = "achievement"
    CHALLENGE = "challenge"
    LEARNING_PATH = "learning_path"


class QuestStatus(str, Enum):
    """Statut d'une quête"""
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REWARDED = "rewarded"


class QuestRequirement(BaseModel):
    """Requirement pour compléter une quête"""
    type: str  # "complete_modules", "score_threshold", "time_spent", etc.
    target: Any  # Valeur cible
    current: Any = 0  # Valeur actuelle


class Quest(BaseModel):
    """Modèle d'une quête"""
    id: str
    title: str
    description: str
    quest_type: QuestType
    requirements: List[QuestRequirement]
    rewards: Dict[str, Any]  # Points, badges, etc.
    difficulty: Difficulty
    subject: Optional[Subject] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True


class UserQuest(BaseModel):
    """Quête d'un utilisateur"""
    id: str
    user_id: str
    quest_id: str
    status: QuestStatus
    progress: Dict[str, Any]  # Progression actuelle
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True


class LeaderboardEntry(BaseModel):
    """Entrée dans un classement"""
    user_id: str
    username: str
    score: float
    rank: int
    badge: Optional[str] = None
    
    class Config:
        from_attributes = True


class Challenge(BaseModel):
    """Défi personnalisé"""
    id: str
    user_id: str
    title: str
    description: str
    target: Dict[str, Any]  # Objectif du défi
    current: Dict[str, Any] = {}  # Progression actuelle
    difficulty: Difficulty
    deadline: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True











