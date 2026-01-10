"""
Service pour la gestion des Travaux Pratiques (TP) - Business logic
"""
from typing import Dict, Any, List
from app.repositories.tp_repository import TPRepository
from app.repositories.module_repository import ModuleRepository
from app.models import TPCreate
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class TPService:
    """Service pour la gestion des TP"""

    @staticmethod
    async def get_tps_by_module(module_id: str) -> List[Dict[str, Any]]:
        """Récupère tous les TP d'un module"""
        # Vérifier que le module existe
        module = await ModuleRepository.find_by_id(module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Module non trouvé")
        
        return await TPRepository.find_by_module_id(module_id)

    @staticmethod
    async def get_tp(tp_id: str) -> Dict[str, Any]:
        """Récupère un TP par son ID"""
        tp = await TPRepository.find_by_id(tp_id)
        if not tp:
            raise HTTPException(status_code=404, detail="TP non trouvé")
        return tp

    @staticmethod
    async def create_tp(tp_data: TPCreate) -> Dict[str, Any]:
        """Crée un nouveau TP"""
        # Vérifier que le module existe
        module = await ModuleRepository.find_by_id(tp_data.module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Module non trouvé")

        tp_dict = tp_data.dict()
        return await TPRepository.create(tp_dict)

    @staticmethod
    async def update_tp(tp_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Met à jour un TP"""
        tp = await TPRepository.update(tp_id, update_data)
        if not tp:
            raise HTTPException(status_code=404, detail="TP non trouvé")
        return tp

    @staticmethod
    async def delete_tp(tp_id: str) -> bool:
        """Supprime un TP"""
        return await TPRepository.delete(tp_id)














