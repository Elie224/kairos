"""
Modèles pour le générateur de parcours intelligent
"""
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from app.models import Subject, Difficulty


class PathwayStatus(str, Enum):
    """Statut d'un parcours"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


class PathwayType(str, Enum):
    """Type de parcours"""
    LINEAR = "linear"  # Parcours linéaire séquentiel
    BRANCHED = "branched"  # Parcours avec branches conditionnelles
    ADAPTIVE = "adaptive"  # Parcours adaptatif selon performances
    CUSTOM = "custom"  # Parcours personnalisé


class PrerequisiteLevel(str, Enum):
    """Niveau de prérequis"""
    REQUIRED = "required"  # Obligatoire
    RECOMMENDED = "recommended"  # Recommandé
    OPTIONAL = "optional"  # Optionnel


class PathwayModule(BaseModel):
    """Module dans un parcours"""
    module_id: str
    order: int  # Ordre dans le parcours
    prerequisite_level: PrerequisiteLevel = PrerequisiteLevel.REQUIRED
    unlock_condition: Optional[Dict[str, Any]] = None  # Condition pour débloquer
    estimated_time: int  # Temps estimé en minutes
    required_score: Optional[float] = None  # Score minimum requis pour continuer


class PathwayCreate(BaseModel):
    """Modèle pour créer un parcours"""
    title: str
    description: str
    subject: Subject
    target_level: Difficulty
    pathway_type: PathwayType = PathwayType.ADAPTIVE
    learning_objectives: List[str]
    modules: List[PathwayModule]
    estimated_duration: int  # Durée totale estimée en heures
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or len(v.strip()) < 3:
            raise ValueError("Le titre doit contenir au moins 3 caractères")
        if len(v) > 200:
            raise ValueError("Le titre ne peut pas dépasser 200 caractères")
        return v.strip()
    
    @field_validator('modules')
    @classmethod
    def validate_modules(cls, v: List[PathwayModule]) -> List[PathwayModule]:
        if not v or len(v) == 0:
            raise ValueError("Un parcours doit contenir au moins un module")
        if len(v) > 50:
            raise ValueError("Un parcours ne peut pas contenir plus de 50 modules")
        return v


class Pathway(BaseModel):
    """Modèle complet d'un parcours"""
    id: str
    title: str
    description: str
    subject: Subject
    target_level: Difficulty
    pathway_type: PathwayType
    learning_objectives: List[str]
    modules: List[PathwayModule]
    estimated_duration: int
    status: PathwayStatus
    created_by: Optional[str] = None  # ID utilisateur créateur
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True


class PathwayProgress(BaseModel):
    """Progression d'un utilisateur dans un parcours"""
    id: str
    user_id: str
    pathway_id: str
    current_module_index: int  # Index du module actuel
    completed_modules: List[str]  # IDs des modules complétés
    started_at: datetime
    completed_at: Optional[datetime] = None
    progress_percentage: float  # Pourcentage de complétion (0-100)
    estimated_remaining_time: int  # Temps restant estimé en minutes
    
    class Config:
        from_attributes = True


class PathwayRecommendation(BaseModel):
    """Recommandation de parcours pour un utilisateur"""
    pathway_id: str
    pathway_title: str
    match_score: float  # Score de correspondance (0-1)
    reasoning: str  # Explication de la recommandation
    estimated_time: int  # Temps estimé en heures
    difficulty_match: bool  # Si la difficulté correspond au niveau
    prerequisites_met: bool  # Si les prérequis sont satisfaits


class PrerequisiteAnalysis(BaseModel):
    """Analyse des prérequis pour un module"""
    module_id: str
    missing_prerequisites: List[str]  # IDs des modules prérequis manquants
    satisfied_prerequisites: List[str]  # IDs des prérequis satisfaits
    prerequisite_score: float  # Score de prérequis (0-1)
    recommendation: str  # Recommandation basée sur l'analyse











