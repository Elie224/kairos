"""
Service pour la gestion des Ressources de cours - Business logic
"""
from typing import Dict, Any, List
from app.repositories.resource_repository import ResourceRepository
from app.repositories.module_repository import ModuleRepository
from app.models import ResourceCreate
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class ResourceService:
    """Service pour la gestion des ressources"""

    @staticmethod
    async def get_resources_by_module(module_id: str) -> List[Dict[str, Any]]:
        """Récupère toutes les ressources d'un module"""
        # Vérifier que le module existe
        module = await ModuleRepository.find_by_id(module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Module non trouvé")
        
        return await ResourceRepository.find_by_module_id(module_id)

    @staticmethod
    async def get_resource(resource_id: str) -> Dict[str, Any]:
        """Récupère une ressource par son ID"""
        resource = await ResourceRepository.find_by_id(resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Ressource non trouvée")
        return resource

    @staticmethod
    async def create_resource(resource_data: ResourceCreate) -> Dict[str, Any]:
        """Crée une nouvelle ressource"""
        # Vérifier que le module existe
        module = await ModuleRepository.find_by_id(resource_data.module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Module non trouvé")

        # Valider que soit file_url soit external_url est fourni selon le type
        if resource_data.resource_type.value == "link":
            if not resource_data.external_url:
                raise HTTPException(status_code=400, detail="Une URL externe est requise pour les liens")
        else:
            if not resource_data.file_url:
                raise HTTPException(status_code=400, detail="Un fichier est requis pour ce type de ressource")

        from datetime import timezone, datetime
        resource_dict = resource_data.dict()
        resource_dict["created_at"] = datetime.now(timezone.utc)
        resource_dict["updated_at"] = datetime.now(timezone.utc)
        return await ResourceRepository.create(resource_dict)

    @staticmethod
    async def update_resource(resource_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Met à jour une ressource"""
        from datetime import timezone, datetime
        update_data["updated_at"] = datetime.now(timezone.utc)
        resource = await ResourceRepository.update(resource_id, update_data)
        if not resource:
            raise HTTPException(status_code=404, detail="Ressource non trouvée")
        return resource

    @staticmethod
    async def delete_resource(resource_id: str) -> bool:
        """Supprime une ressource"""
        return await ResourceRepository.delete(resource_id)








