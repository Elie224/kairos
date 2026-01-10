"""
Service pour la gestion des Travaux Dirigés (TD) - Business logic
"""
from typing import Dict, Any, List
from app.repositories.td_repository import TDRepository
from app.repositories.module_repository import ModuleRepository
from app.models import TDCreate
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class TDService:
    """Service pour la gestion des TD"""

    @staticmethod
    async def get_tds_by_module(module_id: str) -> List[Dict[str, Any]]:
        """Récupère tous les TD d'un module"""
        # Vérifier que le module existe
        module = await ModuleRepository.find_by_id(module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Module non trouvé")
        
        return await TDRepository.find_by_module_id(module_id)

    @staticmethod
    async def get_td(td_id: str) -> Dict[str, Any]:
        """Récupère un TD par son ID"""
        td = await TDRepository.find_by_id(td_id)
        if not td:
            raise HTTPException(status_code=404, detail="TD non trouvé")
        return td

    @staticmethod
    async def create_td(td_data: TDCreate) -> Dict[str, Any]:
        """Crée un nouveau TD"""
        # Vérifier que le module existe
        module = await ModuleRepository.find_by_id(td_data.module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Module non trouvé")

        td_dict = td_data.dict()
        return await TDRepository.create(td_dict)

    @staticmethod
    async def update_td(td_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Met à jour un TD"""
        td = await TDRepository.update(td_id, update_data)
        if not td:
            raise HTTPException(status_code=404, detail="TD non trouvé")
        return td

    @staticmethod
    async def delete_td(td_id: str) -> bool:
        """Supprime un TD"""
        return await TDRepository.delete(td_id)














