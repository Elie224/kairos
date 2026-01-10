"""
Service pour la gestion des validations de module - Business logic
"""
from typing import Dict, Any, Optional, List
from app.repositories.validation_repository import ValidationRepository
from app.repositories.exam_repository import ExamAttemptRepository
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class ValidationService:
    """Service pour la gestion des validations de module"""

    @staticmethod
    async def validate_module(
        user_id: str,
        module_id: str,
        exam_attempt_id: str,
        score: float
    ) -> bool:
        """
        Valide un module pour un utilisateur après réussite d'un examen
        """
        try:
            # Vérifier si le module est déjà validé
            existing = await ValidationRepository.find_by_user_and_module(user_id, module_id)
            if existing:
                logger.info(f"Le module {module_id} est déjà validé pour l'utilisateur {user_id}")
                return True

            # Vérifier que la tentative d'examen existe et est réussie
            attempt = await ExamAttemptRepository.find_by_id(exam_attempt_id)
            if not attempt:
                raise HTTPException(
                    status_code=404,
                    detail="Tentative d'examen non trouvée"
                )

            if not attempt.get("passed"):
                raise HTTPException(
                    status_code=400,
                    detail="L'examen doit être réussi pour valider le module"
                )

            if attempt.get("user_id") != user_id:
                raise HTTPException(
                    status_code=403,
                    detail="Cette tentative d'examen ne vous appartient pas"
                )

            # Créer la validation
            validation_data = {
                "user_id": user_id,
                "module_id": module_id,
                "exam_attempt_id": exam_attempt_id,
                "score": score
            }

            await ValidationRepository.create(validation_data)
            logger.info(f"Module {module_id} validé pour l'utilisateur {user_id} avec un score de {score}%")

            # Attribuer un badge si c'est la première validation
            try:
                from app.services.badge_service import BadgeService
                await BadgeService.check_and_award_badges(user_id)
            except Exception as e:
                logger.warning(f"Erreur lors de l'attribution du badge: {e}")

            return True

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la validation du module: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de la validation du module: {str(e)}"
            )

    @staticmethod
    async def get_user_validations(user_id: str) -> List[Dict[str, Any]]:
        """
        Récupère toutes les validations d'un utilisateur
        """
        try:
            return await ValidationRepository.find_by_user(user_id)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des validations: {e}")
            raise

    @staticmethod
    async def get_module_validation(user_id: str, module_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère la validation d'un module spécifique pour un utilisateur
        """
        try:
            return await ValidationRepository.find_by_user_and_module(user_id, module_id)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la validation: {e}")
            raise

    @staticmethod
    async def is_module_validated(user_id: str, module_id: str) -> bool:
        """
        Vérifie si un module est validé pour un utilisateur
        """
        try:
            return await ValidationRepository.exists(user_id, module_id)
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la validation: {e}")
            return False

    @staticmethod
    async def get_validated_modules(user_id: str) -> List[str]:
        """
        Récupère la liste des modules validés par un utilisateur
        """
        try:
            return await ValidationRepository.get_validated_modules(user_id)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des modules validés: {e}")
            return []
