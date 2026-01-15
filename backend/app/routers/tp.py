"""
Routeur pour les Travaux Pratiques (TP)
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import List
from pathlib import Path
from app.models import TP, TPCreate
from app.services.tp_service import TPService
# Authentification supprimée - toutes les routes sont publiques
from app.utils.security import InputSanitizer
from app.database import get_database
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Dossier pour les PDF (utiliser le même que dans pdf_generator_service)
from app.services.pdf_generator_service import PDF_DIR


@router.get("/module/{module_id}", response_model=List[TP])
async def get_module_tps(
    module_id: str
):
    """Récupère tous les TP d'un module (route publique)"""
    sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
    if not sanitized_module_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")
    
    return await TPService.get_tps_by_module(sanitized_module_id)


@router.get("/{tp_id}", response_model=TP)
async def get_tp(
    tp_id: str
):
    """Récupère un TP spécifique (route publique)"""
    sanitized_id = InputSanitizer.sanitize_object_id(tp_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de TP invalide")
    
    return await TPService.get_tp(sanitized_id)


@router.post("/", response_model=TP, status_code=201)
async def create_tp(
    tp_data: TPCreate
):
    """Crée un nouveau TP (route publique)"""
    sanitized_module_id = InputSanitizer.sanitize_object_id(tp_data.module_id)
    if not sanitized_module_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")
    
    tp_data.module_id = sanitized_module_id
    return await TPService.create_tp(tp_data)


@router.put("/{tp_id}", response_model=TP)
async def update_tp(
    tp_id: str,
    update_data: TPCreate
):
    """Met à jour un TP (route publique)"""
    sanitized_id = InputSanitizer.sanitize_object_id(tp_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de TP invalide")
    
    return await TPService.update_tp(sanitized_id, update_data.dict(exclude_unset=True))


@router.delete("/{tp_id}", status_code=204)
async def delete_tp(
    tp_id: str,
    admin_user: dict = Depends(require_admin)
):
    """Supprime un TP (admin seulement)"""
    sanitized_id = InputSanitizer.sanitize_object_id(tp_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de TP invalide")
    
    success = await TPService.delete_tp(sanitized_id)
    if not success:
        raise HTTPException(status_code=404, detail="TP non trouvé")
    
    return None


@router.get("/{tp_id}/pdf")
async def download_tp_pdf(
    tp_id: str
):
    """Télécharge le PDF d'un TP (route publique)"""
    sanitized_id = InputSanitizer.sanitize_object_id(tp_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de TP invalide")
    
    # Récupérer le TP
    tp = await TPService.get_tp(sanitized_id)
    if not tp:
        raise HTTPException(status_code=404, detail="TP non trouvé")
    
    # Vérifier si le TP a un pdf_url directement
    pdf_url = tp.get("pdf_url")
    
    if not pdf_url:
        # Chercher la ressource PDF associée par titre (fallback)
        db = get_database()
        from bson import ObjectId
        resource = await db.resources.find_one({
            "module_id": ObjectId(tp.get("module_id")) if isinstance(tp.get("module_id"), str) else tp.get("module_id"),
            "resource_type": "pdf",
            "title": {"$regex": f"TP.*{tp.get('title', '')}", "$options": "i"}
        })
        
        if not resource or not resource.get("file_url"):
            raise HTTPException(status_code=404, detail="PDF non trouvé pour ce TP")
        
        pdf_url = resource.get("file_url")
    
    # Extraire le nom du fichier de l'URL
    filename = Path(pdf_url).name
    file_path = PDF_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Fichier PDF non trouvé: {file_path}")
    
    download_filename = f"TP_{tp.get('title', 'tp')}.pdf".replace(" ", "_")
    
    return FileResponse(
        path=str(file_path),
        filename=download_filename,
        media_type="application/pdf"
    )














