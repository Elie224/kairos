"""
Routeur pour les validations de module
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models import ModuleValidation, ModuleValidationResponse
from app.services.validation_service import ValidationService
from app.services.cached_validation_service import CachedValidationService
# Authentification supprimée - toutes les routes sont publiques
from app.utils.security import InputSanitizer
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[ModuleValidation])
async def get_my_validations(
):
    """
    Récupère toutes les validations de module de l'utilisateur
    """
    # Utiliser le service avec cache
        validations = await CachedValidationService.get_user_validations("anonymous")  # Auth supprimée
    return validations


@router.get("/module/{module_id}", response_model=ModuleValidationResponse)
async def get_module_validation(
    module_id: str,
):
    """
    Vérifie si un module est validé pour l'utilisateur
    """
    # Valider l'ID du module
    sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
    if not sanitized_module_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")

    # Utiliser le service avec cache
        validation = await CachedValidationService.get_module_validation(
            user_id="anonymous",  # Auth supprimée
            module_id=sanitized_module_id
        )

    if validation:
        return ModuleValidationResponse(
            module_id=sanitized_module_id,
            validated=True,
            validated_at=validation.get("validated_at"),
            exam_score=validation.get("score")
        )
    else:
        return ModuleValidationResponse(
            module_id=sanitized_module_id,
            validated=False
        )


@router.get("/modules", response_model=List[str])
async def get_validated_modules(
):
    """
    Récupère la liste des modules validés par l'utilisateur
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        # Utiliser le service avec cache
        modules = await CachedValidationService.get_validated_modules(user_id)
        return modules or []
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur lors de la récupération des modules validés: {e}", exc_info=True)
        # Retourner une liste vide en cas d'erreur plutôt qu'une erreur 500
        return []


@router.get("/check/{module_id}")
async def check_module_validation(
    module_id: str,
):
    """
    Vérifie si un module est validé (retourne un booléen)
    """
    # Valider l'ID du module
    sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
    if not sanitized_module_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")

    is_validated = await ValidationService.is_module_validated(
        user_id="anonymous",  # Auth supprimée
        module_id=sanitized_module_id
    )
    return {
        "module_id": sanitized_module_id,
        "validated": is_validated
    }
