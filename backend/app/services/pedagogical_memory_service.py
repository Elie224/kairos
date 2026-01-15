"""
Service pour la gestion de la mémoire pédagogique utilisateur
"""
from typing import Optional, Dict, Any
from app.repositories.pedagogical_memory_repository import PedagogicalMemoryRepository
import logging

logger = logging.getLogger(__name__)


class PedagogicalMemoryService:
    """Service pour la gestion de la mémoire pédagogique"""
    
    @staticmethod
    async def get_memory(user_id: str) -> Optional[Dict[str, Any]]:
        """Récupère la mémoire pédagogique d'un utilisateur"""
        try:
            return await PedagogicalMemoryRepository.find_by_user(user_id)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la mémoire: {e}")
            return None
    
    @staticmethod
    async def get_subject_level(user_id: str, subject: str) -> str:
        """Récupère le niveau d'un utilisateur pour une matière"""
        try:
            memory = await PedagogicalMemoryRepository.find_by_user(user_id)
            if memory and "subject_levels" in memory:
                subject_levels = memory.get("subject_levels", {})
                if subject in subject_levels:
                    return subject_levels[subject].get("level", "beginner")
            return "beginner"
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du niveau: {e}")
            return "beginner"
    
    @staticmethod
    async def get_learning_style(user_id: str) -> Dict[str, Any]:
        """Récupère le style d'apprentissage préféré"""
        try:
            memory = await PedagogicalMemoryRepository.find_by_user(user_id)
            if memory and "learning_style" in memory:
                return memory.get("learning_style", {})
            return {
                "preferred_format": "balanced",
                "detail_level": "medium",
                "examples_preference": True,
                "visual_aids_preference": True
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du style: {e}")
            return {
                "preferred_format": "balanced",
                "detail_level": "medium",
                "examples_preference": True,
                "visual_aids_preference": True
            }
    
    @staticmethod
    async def get_frequent_errors(user_id: str, limit: int = 5) -> list:
        """Récupère les erreurs fréquentes d'un utilisateur"""
        try:
            memory = await PedagogicalMemoryRepository.find_by_user(user_id)
            if memory and "error_history" in memory:
                error_history = memory.get("error_history", [])
                # Trier par nombre d'erreurs décroissant
                sorted_errors = sorted(
                    error_history,
                    key=lambda x: x.get("error_count", 0),
                    reverse=True
                )
                return sorted_errors[:limit]
            return []
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des erreurs: {e}")
            return []
    
    @staticmethod
    async def record_error(user_id: str, concept: str, error_type: str):
        """Enregistre une erreur dans la mémoire"""
        try:
            await PedagogicalMemoryRepository.add_error(user_id, concept, error_type)
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement d'erreur: {e}")
    
    @staticmethod
    async def update_level(user_id: str, subject: str, level: str, confidence_score: float = 0.5):
        """Met à jour le niveau d'un utilisateur pour une matière"""
        try:
            await PedagogicalMemoryRepository.update_subject_level(
                user_id, subject, level, confidence_score
            )
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du niveau: {e}")
    
    @staticmethod
    async def adapt_explanation(user_id: str, subject: str) -> Dict[str, Any]:
        """Adapte l'explication selon la mémoire pédagogique"""
        try:
            memory = await PedagogicalMemoryService.get_memory(user_id)
            level = await PedagogicalMemoryService.get_subject_level(user_id, subject)
            learning_style = await PedagogicalMemoryService.get_learning_style(user_id)
            frequent_errors = await PedagogicalMemoryService.get_frequent_errors(user_id, 3)
            
            # Déterminer le niveau de détail
            detail_level = learning_style.get("detail_level", "medium")
            if level == "beginner":
                detail_level = "high"
            elif level == "advanced":
                detail_level = "low"
            
            # Déterminer le format préféré
            preferred_format = learning_style.get("preferred_format", "balanced")
            
            # Construire le contexte d'adaptation
            adaptation = {
                "level": level,
                "detail_level": detail_level,
                "preferred_format": preferred_format,
                "examples_preferred": learning_style.get("examples_preference", True),
                "visual_aids_preferred": learning_style.get("visual_aids_preference", True),
                "frequent_errors": [err.get("concept") for err in frequent_errors],
                "explanation_length": memory.get("preferred_explanation_length", "medium") if memory else "medium"
            }
            
            return adaptation
        except Exception as e:
            logger.error(f"Erreur lors de l'adaptation de l'explication: {e}")
            return {
                "level": "beginner",
                "detail_level": "medium",
                "preferred_format": "balanced",
                "examples_preferred": True,
                "visual_aids_preferred": True,
                "frequent_errors": [],
                "explanation_length": "medium"
            }
