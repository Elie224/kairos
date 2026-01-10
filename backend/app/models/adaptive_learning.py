"""
Modèles pour l'IA pédagogique adaptative
"""
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from app.models import Difficulty, Subject


class CognitiveProfile(str, Enum):
    """Profil cognitif de l'apprenant"""
    VISUAL = "visual"  # Apprend mieux visuellement
    AUDITORY = "auditory"  # Apprend mieux auditivement
    KINESTHETIC = "kinesthetic"  # Apprend mieux par la pratique
    READING = "reading"  # Apprend mieux par la lecture
    MIXED = "mixed"  # Profil mixte


class LearningStyle(str, Enum):
    """Style d'apprentissage"""
    SEQUENTIAL = "sequential"  # Apprentissage séquentiel
    GLOBAL = "global"  # Vue d'ensemble d'abord
    ACTIVE = "active"  # Apprentissage actif
    REFLECTIVE = "reflective"  # Apprentissage réfléchi


class PerformanceLevel(str, Enum):
    """Niveau de performance"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class AdaptiveDiagnostic(BaseModel):
    """Résultat du diagnostic adaptatif initial"""
    user_id: str
    initial_level: PerformanceLevel
    cognitive_profile: CognitiveProfile
    learning_style: LearningStyle
    strengths: List[str]  # Points forts identifiés
    weaknesses: List[str]  # Points faibles identifiés
    recommended_difficulty: Difficulty
    estimated_time_per_module: int  # en minutes
    diagnostic_score: float  # Score du diagnostic (0-100)
    completed_at: datetime


class LearningProfile(BaseModel):
    """Profil d'apprentissage de l'utilisateur"""
    id: str
    user_id: str
    current_level: PerformanceLevel
    cognitive_profile: CognitiveProfile
    learning_style: LearningStyle
    
    # Métriques d'apprentissage
    average_response_time: float  # Temps moyen de réponse en secondes
    accuracy_rate: float  # Taux de précision (0-1)
    completion_rate: float  # Taux de complétion (0-1)
    engagement_score: float  # Score d'engagement (0-1)
    
    # Adaptation dynamique
    current_difficulty: Difficulty
    difficulty_history: List[Dict[str, Any]]  # Historique des ajustements
    adaptation_frequency: int  # Nombre d'ajustements effectués
    
    # Préférences
    preferred_explanation_type: str  # "visual", "textual", "step_by_step"
    preferred_exercise_format: str  # "quiz", "exercises", "simulations"
    
    # Statistiques par matière
    subject_performance: Dict[str, Dict[str, Any]]  # Performance par Subject
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True


class AdaptiveRecommendation(BaseModel):
    """Recommandation adaptative pour l'utilisateur"""
    user_id: str
    module_id: Optional[str] = None
    recommendation_type: str  # "difficulty_adjustment", "content_suggestion", "pace_adjustment"
    current_state: Dict[str, Any]
    recommended_state: Dict[str, Any]
    reasoning: str  # Explication de la recommandation
    confidence_score: float  # Confiance dans la recommandation (0-1)
    created_at: datetime


class DifficultyAdjustment(BaseModel):
    """Ajustement de difficulté"""
    user_id: str
    module_id: str
    previous_difficulty: Difficulty
    new_difficulty: Difficulty
    reason: str  # Raison de l'ajustement
    performance_data: Dict[str, Any]  # Données de performance ayant mené à l'ajustement
    adjusted_at: datetime


class AdaptiveContentRequest(BaseModel):
    """Requête pour contenu adaptatif"""
    module_id: str
    user_id: str
    preferred_format: Optional[str] = None  # "visual", "textual", "interactive"
    difficulty_override: Optional[Difficulty] = None


class AdaptiveContentResponse(BaseModel):
    """Réponse avec contenu adaptatif"""
    module_id: str
    adapted_content: Dict[str, Any]  # Contenu adapté selon le profil
    explanation_style: str  # Style d'explication utilisé
    difficulty_level: Difficulty
    estimated_time: int  # Temps estimé en minutes
    learning_objectives: List[str]  # Objectifs adaptés
    adaptation_notes: str  # Notes sur les adaptations effectuées











