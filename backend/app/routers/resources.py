"""
Routeur pour les Ressources de cours
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List, Optional
from app.models import Resource, ResourceCreate, ResourceType
from app.services.resource_service import ResourceService
# Authentification supprimée - toutes les routes sont publiques
from app.utils.security import InputSanitizer
from app.database import get_database
import os
import uuid
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Configuration du dossier d'upload
UPLOAD_DIR = Path("uploads/resources")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# S'assurer que le dossier existe et est accessible
if not UPLOAD_DIR.exists():
    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Dossier d'upload créé: {UPLOAD_DIR.absolute()}")
    except Exception as e:
        logger.error(f"Impossible de créer le dossier d'upload: {e}")

# Types de fichiers autorisés
ALLOWED_EXTENSIONS = {
    "pdf": [".pdf"],
    "word": [".doc", ".docx"],
    "ppt": [".ppt", ".pptx"],
    "video": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"]
}

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


def get_file_extension(filename: str) -> str:
    """Extrait l'extension du fichier"""
    return Path(filename).suffix.lower()


def is_allowed_file(filename: str, resource_type: str) -> bool:
    """Vérifie si le type de fichier est autorisé"""
    if resource_type == "link":
        return True
    ext = get_file_extension(filename)
    allowed = ALLOWED_EXTENSIONS.get(resource_type, [])
    return ext in allowed


@router.get("/module/{module_id}", response_model=List[Resource])
async def get_module_resources(
    module_id: str,
):
    """Récupère toutes les ressources d'un module"""
    sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
    if not sanitized_module_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")
    
    return await ResourceService.get_resources_by_module(sanitized_module_id)


@router.get("/files/{filename}")
async def download_resource_file(
    filename: str,
):
    """Télécharge un fichier de ressource (route publique)"""
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    # Essayer de trouver la ressource pour obtenir le nom original du fichier
    try:
        db = get_database()
        resource = await db.resources.find_one({"file_url": {"$regex": filename}})
        if resource and resource.get("file_name"):
            download_filename = resource["file_name"]
        else:
            download_filename = filename
    except Exception as e:
        logger.warning(f"Impossible de récupérer le nom original du fichier: {e}")
        download_filename = filename
    
    # Déterminer le type MIME selon l'extension
    file_ext = get_file_extension(filename)
    media_type_map = {
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".ppt": "application/vnd.ms-powerpoint",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".mp4": "video/mp4",
        ".avi": "video/x-msvideo",
        ".mov": "video/quicktime",
        ".wmv": "video/x-ms-wmv",
        ".flv": "video/x-flv",
        ".webm": "video/webm",
    }
    media_type = media_type_map.get(file_ext, "application/octet-stream")
    
    return FileResponse(
        path=str(file_path),
        filename=download_filename,
        media_type=media_type
    )


@router.get("/{resource_id}", response_model=Resource)
async def get_resource(
    resource_id: str,
):
    """Récupère une ressource par son ID (route publique)"""
    sanitized_id = InputSanitizer.sanitize_object_id(resource_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de ressource invalide")
    
    return await ResourceService.get_resource(sanitized_id)


@router.post("/upload", response_model=Resource, status_code=201)
async def upload_resource(
    module_id: str = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(default=None),
    resource_type: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload un fichier et crée une ressource (route publique)"""
    # Convertir les chaînes vides en None pour les champs optionnels
    if description is not None and description.strip() == "":
        description = None
    
    logger.info(f"Upload de ressource - module_id: {module_id}, title: {title}, resource_type: {resource_type}, description: {description}")
    
    # Vérifier que le fichier a un nom
    if not file.filename:
        logger.error("Le fichier n'a pas de nom")
        raise HTTPException(status_code=400, detail="Le fichier doit avoir un nom")
    
    logger.info(f"Nom du fichier: {file.filename}")
    
    # Valider le type de ressource
    try:
        res_type = ResourceType(resource_type)
    except ValueError as e:
        logger.error(f"Type de ressource invalide: {resource_type}, erreur: {e}")
        raise HTTPException(status_code=400, detail=f"Type de ressource invalide: {resource_type}")
    
    # Vérifier que le type correspond au fichier
    if not is_allowed_file(file.filename, resource_type):
        raise HTTPException(
            status_code=400,
            detail=f"Type de fichier non autorisé pour {resource_type}. Extensions autorisées: {ALLOWED_EXTENSIONS.get(resource_type, [])}"
        )
    
    # Vérifier la taille du fichier
    file_content = await file.read()
    file_size = len(file_content)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Fichier trop volumineux. Taille maximale: {MAX_FILE_SIZE / (1024 * 1024)} MB"
        )
    
    # Générer un nom de fichier unique
    file_ext = get_file_extension(file.filename)
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # Sauvegarder le fichier
    try:
        # S'assurer que le dossier existe
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        file_path = UPLOAD_DIR / unique_filename
        
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        logger.info(f"Fichier sauvegardé: {file_path.absolute()}")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du fichier: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde du fichier: {str(e)}")
    
    # Sanitizer le module_id
    sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
    if not sanitized_module_id:
        logger.error(f"ID de module invalide: {module_id}")
        raise HTTPException(status_code=400, detail="ID de module invalide")
    
    logger.info(f"Module ID sanitizé: {sanitized_module_id}")
    
    # Créer la ressource
    try:
        resource_data = ResourceCreate(
            module_id=sanitized_module_id,
            title=title,
            description=description,
            resource_type=res_type,
            file_url=f"/api/resources/files/{unique_filename}",
            file_size=file_size,
            file_name=file.filename
        )
        logger.info(f"Données de ressource créées: {resource_data.dict()}")
        
        result = await ResourceService.create_resource(resource_data)
        logger.info(f"Ressource créée avec succès: {result.get('id')}")
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la création de la ressource: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la ressource: {str(e)}")


@router.post("/link", response_model=Resource, status_code=201)
async def create_link_resource(
    resource_data: ResourceCreate,
):
    """Crée une ressource de type lien (route publique)"""
    # Forcer le type à LINK
    resource_data.resource_type = ResourceType.LINK
    
    # Sanitizer le module_id
    sanitized_module_id = InputSanitizer.sanitize_object_id(resource_data.module_id)
    if not sanitized_module_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")
    resource_data.module_id = sanitized_module_id
    
    # Vérifier que l'URL externe est fournie
    if not resource_data.external_url:
        raise HTTPException(status_code=400, detail="Une URL externe est requise pour les liens")
    
    return await ResourceService.create_resource(resource_data)


@router.put("/{resource_id}", response_model=Resource)
async def update_resource(
    resource_id: str,
    update_data: dict,
):
    """Met à jour une ressource (route publique)"""
    sanitized_id = InputSanitizer.sanitize_object_id(resource_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de ressource invalide")
    
    return await ResourceService.update_resource(sanitized_id, update_data)


@router.delete("/{resource_id}", status_code=204)
async def delete_resource(
    resource_id: str,
):
    """Supprime une ressource (route publique)"""
    sanitized_id = InputSanitizer.sanitize_object_id(resource_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de ressource invalide")
    
    # Récupérer la ressource pour supprimer le fichier associé
    resource = await ResourceService.get_resource(sanitized_id)
    if resource.get("file_url"):
        file_path = UPLOAD_DIR / Path(resource["file_url"]).name
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                logger.error(f"Erreur lors de la suppression du fichier: {e}")
    
    await ResourceService.delete_resource(sanitized_id)
    return None

