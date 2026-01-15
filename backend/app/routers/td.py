"""
Routeur pour les Travaux Dirigés (TD)
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import List
from pathlib import Path
from bson import ObjectId
from app.models import TD, TDCreate
from app.services.td_service import TDService
# Authentification supprimée - toutes les routes sont publiques
from app.utils.security import InputSanitizer
from app.database import get_database
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Dossier pour les PDF (utiliser le même que dans pdf_generator_service)
from app.services.pdf_generator_service import PDF_DIR


@router.get("/module/{module_id}", response_model=List[TD])
async def get_module_tds(
    module_id: str
):
    """Récupère tous les TD d'un module (route publique)"""
    sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
    if not sanitized_module_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")
    
    return await TDService.get_tds_by_module(sanitized_module_id)


@router.get("/{td_id}", response_model=TD)
async def get_td(
    td_id: str
):
    """Récupère un TD spécifique (route publique)"""
    sanitized_id = InputSanitizer.sanitize_object_id(td_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de TD invalide")
    
    return await TDService.get_td(sanitized_id)


@router.post("/", response_model=TD, status_code=201)
async def create_td(
    td_data: TDCreate
):
    """Crée un nouveau TD (route publique)"""
    sanitized_module_id = InputSanitizer.sanitize_object_id(td_data.module_id)
    if not sanitized_module_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")
    
    td_data.module_id = sanitized_module_id
    return await TDService.create_td(td_data)


@router.put("/{td_id}", response_model=TD)
async def update_td(
    td_id: str,
    update_data: TDCreate
):
    """Met à jour un TD (route publique)"""
    sanitized_id = InputSanitizer.sanitize_object_id(td_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de TD invalide")
    
    return await TDService.update_td(sanitized_id, update_data.dict(exclude_unset=True))


@router.delete("/{td_id}", status_code=204)
async def delete_td(
    td_id: str
):
    """Supprime un TD (admin seulement)"""
    sanitized_id = InputSanitizer.sanitize_object_id(td_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de TD invalide")
    
    success = await TDService.delete_td(sanitized_id)
    if not success:
        raise HTTPException(status_code=404, detail="TD non trouvé")
    
    return None


@router.get("/{td_id}/pdf")
async def download_td_pdf(
    td_id: str
):
    """Télécharge le PDF d'un TD (route publique)"""
    sanitized_id = InputSanitizer.sanitize_object_id(td_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de TD invalide")
    
    # Récupérer le TD
    td = await TDService.get_td(sanitized_id)
    if not td:
        raise HTTPException(status_code=404, detail="TD non trouvé")
    
    # Vérifier si le TD a un pdf_url directement
    pdf_url = td.get("pdf_url")
    
    if not pdf_url:
        # Chercher la ressource PDF associée par titre (fallback)
        db = get_database()
        resource = await db.resources.find_one({
            "module_id": ObjectId(td.get("module_id")) if isinstance(td.get("module_id"), str) else td.get("module_id"),
            "resource_type": "pdf",
            "title": {"$regex": f"TD.*{td.get('title', '')}", "$options": "i"}
        })
        
        if not resource or not resource.get("file_url"):
            raise HTTPException(status_code=404, detail="PDF non trouvé pour ce TD")
        
        pdf_url = resource.get("file_url")
    
    # Extraire le nom du fichier de l'URL
    filename = Path(pdf_url).name
    file_path = PDF_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Fichier PDF non trouvé: {file_path}")
    
    download_filename = f"TD_{td.get('title', 'td')}.pdf".replace(" ", "_")
    
    return FileResponse(
        path=str(file_path),
        filename=download_filename,
        media_type="application/pdf"
    )














