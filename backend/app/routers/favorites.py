"""
Routeur pour les favoris
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models import Favorite, FavoriteCreate
# Authentification supprimée - toutes les routes sont publiques
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.module_repository import ModuleRepository

router = APIRouter()


@router.post("/", response_model=Favorite, status_code=201)
async def add_favorite(
    favorite_data: FavoriteCreate,
):
    """Ajoute un module aux favoris"""
    from app.utils.security import InputSanitizer
    
    # Valider et sanitizer le module_id
    sanitized_module_id = InputSanitizer.sanitize_object_id(favorite_data.module_id)
    if not sanitized_module_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")
    
    # Vérifier que le module existe
    module = await ModuleRepository.find_by_id(sanitized_module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module non trouvé")
    
    return await FavoriteRepository.create("anonymous", sanitized_module_id)  # Auth supprimée


@router.delete("/{module_id}")
async def remove_favorite(
    module_id: str,
):
    """Retire un module des favoris"""
    from app.utils.security import InputSanitizer
    
    # Valider l'ObjectId
    sanitized_id = InputSanitizer.sanitize_object_id(module_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")
    
    success = await FavoriteRepository.delete("anonymous", sanitized_id)  # Auth supprimée
    if not success:
        raise HTTPException(status_code=404, detail="Favori non trouvé")
    return {"message": "Favori supprimé"}


@router.get("/", response_model=List[Favorite])
async def get_favorites():
    """Récupère tous les favoris de l'utilisateur"""
    return await FavoriteRepository.find_by_user("anonymous")  # Auth supprimée


@router.get("/{module_id}/check")
async def check_favorite(
    module_id: str,
):
    """Vérifie si un module est en favoris"""
    from app.utils.security import InputSanitizer
    
    # Valider l'ObjectId
    sanitized_id = InputSanitizer.sanitize_object_id(module_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")
    
    is_favorite = await FavoriteRepository.is_favorite("anonymous", sanitized_id)  # Auth supprimée
    return {"is_favorite": is_favorite}

