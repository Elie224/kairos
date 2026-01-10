"""
Modèles pour l'historique utilisateur et le cache intelligent
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Subject(str, Enum):
    """Matières disponibles - Version simplifiée pour développement"""
    MATHEMATICS = "mathematics"  # Algèbre
    COMPUTER_SCIENCE = "computer_science"  # Machine Learning


class HistoryEntry(BaseModel):
    """Entrée d'historique utilisateur"""
    user_id: str
    question: str
    answer: str
    subject: Optional[Subject] = None
    module_id: Optional[str] = None
    model_used: str = "gpt-5-mini"
    tokens_used: Optional[int] = None
    cost_eur: Optional[float] = None
    language: str = "fr"
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HistoryQuery(BaseModel):
    """Requête pour récupérer l'historique"""
    user_id: str
    subject: Optional[Subject] = None
    module_id: Optional[str] = None
    limit: int = 50
    offset: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class HistoryStats(BaseModel):
    """Statistiques de l'historique"""
    total_questions: int
    total_tokens: int
    total_cost_eur: float
    by_subject: Dict[str, int]
    by_model: Dict[str, int]
    most_asked_questions: List[Dict[str, Any]]


class SimilarQuestionRequest(BaseModel):
    """Requête pour trouver des questions similaires"""
    question: str
    user_id: Optional[str] = None
    threshold: float = 0.8  # Seuil de similarité (0-1)


class SimilarQuestionResponse(BaseModel):
    """Réponse avec questions similaires"""
    question: str
    similar_questions: List[Dict[str, Any]]
    found_exact_match: bool = False
    exact_match_answer: Optional[str] = None











