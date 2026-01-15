"""
Routeur pour les examens
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from typing import List, Optional
from app.models import (
    Exam, ExamCreate, ExamAttempt, ExamAttemptCreate,
    ExamSubmission, ExamAttemptResponse
)
from app.services.exam_service import ExamService
# PDFService supprimé - fonctionnalité PDF désactivée pour l'instant
from app.utils.permissions import get_current_user, require_admin
from app.utils.security import InputSanitizer
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/module/{module_id}/prerequisites")
async def check_exam_prerequisites(
    module_id: str
):
    """
    Vérifie si l'étudiant peut passer l'examen (route publique)
    """
    # Valider l'ID du module
    sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
    if not sanitized_module_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")

    prerequisites = await ExamService.check_prerequisites("anonymous", sanitized_module_id)  # Auth supprimée
    return prerequisites


@router.get("/module/{module_id}", response_model=Exam)
async def get_module_exam(
    module_id: str,
    num_questions: int = Query(15, ge=5, le=50, description="Nombre de questions"),
    passing_score: float = Query(70.0, ge=0, le=100, description="Score de passage (%)"),
    time_limit: int = Query(30, ge=10, le=180, description="Temps limite (minutes)"),
    force_regenerate: bool = Query(False, description="Forcer la régénération de l'examen")
):
    """
    Récupère l'examen d'un module (génère s'il n'existe pas) (route publique)
    """
    # Valider l'ID du module
    sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
    if not sanitized_module_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")

    # Vérifier les prérequis (toujours autorisé car auth supprimée)
    if not force_regenerate:
        prerequisites = await ExamService.check_prerequisites("anonymous", sanitized_module_id)  # Auth supprimée
        # Ne plus bloquer même si prérequis non satisfaits (auth supprimée)

    exam = await ExamService.get_or_generate_exam(
        module_id=sanitized_module_id,
        num_questions=num_questions,
        passing_score=passing_score,
        time_limit=time_limit,
        force_regenerate=force_regenerate
    )
    return exam


@router.post("/", response_model=Exam, status_code=201)
async def create_exam(
    exam_data: ExamCreate
):
    """
    Crée un nouvel examen (route publique)
    """
    # Valider l'ID du module
    sanitized_module_id = InputSanitizer.sanitize_object_id(exam_data.module_id)
    if not sanitized_module_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")

    exam = await ExamService.get_or_generate_exam(
        module_id=sanitized_module_id,
        num_questions=exam_data.num_questions,
        passing_score=exam_data.passing_score,
        time_limit=exam_data.time_limit
    )
    return exam


@router.post("/start", response_model=ExamAttempt, status_code=201)
async def start_exam(
    attempt_data: ExamAttemptCreate
):
    """
    Démarre une tentative d'examen (route publique)
    """
    # Valider l'ID de l'examen
    sanitized_exam_id = InputSanitizer.sanitize_object_id(attempt_data.exam_id)
    if not sanitized_exam_id:
        raise HTTPException(status_code=400, detail="ID d'examen invalide")

    attempt = await ExamService.start_exam_attempt(
        user_id="anonymous",  # Auth supprimée
        exam_id=sanitized_exam_id
    )
    return attempt


@router.post("/submit", response_model=ExamAttemptResponse)
async def submit_exam(
    submission: ExamSubmission,
    current_user: dict = Depends(get_current_user)
):
    """
    Soumet les réponses d'un examen et calcule le score
    """
    # Valider l'ID de l'examen
    sanitized_exam_id = InputSanitizer.sanitize_object_id(submission.exam_id)
    if not sanitized_exam_id:
        raise HTTPException(status_code=400, detail="ID d'examen invalide")

    submission.exam_id = sanitized_exam_id

    result = await ExamService.submit_exam(
        user_id=current_user["id"],
        submission=submission
    )
    return ExamAttemptResponse(**result)


@router.get("/attempts", response_model=List[ExamAttempt])
async def get_my_exam_attempts(
    module_id: Optional[str] = Query(None, description="Filtrer par module"),
    limit: int = Query(50, ge=1, le=100, description="Limite de résultats")
):
    """
    Récupère toutes les tentatives d'examen (route publique)
    """
    try:
        sanitized_module_id = None
        if module_id:
            sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_module_id:
                raise HTTPException(status_code=400, detail="ID de module invalide")

        attempts = await ExamService.get_user_exam_attempts(
            user_id="anonymous",  # Auth supprimée
            module_id=sanitized_module_id,
            limit=limit
        )
        return attempts or []
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur lors de la récupération des tentatives d'examen: {e}", exc_info=True)
        # Retourner une liste vide en cas d'erreur plutôt qu'une erreur 500
        return []


@router.get("/attempts/{attempt_id}", response_model=ExamAttempt)
async def get_exam_attempt(
    attempt_id: str
):
    """
    Récupère une tentative d'examen spécifique (route publique)
    """
    from app.repositories.exam_repository import ExamAttemptRepository
    
    # Valider l'ID
    sanitized_id = InputSanitizer.sanitize_object_id(attempt_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de tentative invalide")

    attempt = await ExamAttemptRepository.find_by_id(sanitized_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Tentative non trouvée")

    # Plus de vérification d'appartenance (auth supprimée)

    return attempt


@router.get("/module/{module_id}/pdf")
async def download_exam_pdf(
    module_id: str
):
    """
    Télécharge l'examen d'un module en format PDF (route publique)
    """
    from fastapi.responses import FileResponse
    from pathlib import Path
    from bson import ObjectId
    from app.database import get_database
    
    # Valider l'ID du module
    sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
    if not sanitized_module_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")
    
    # Récupérer l'examen
    exam = await ExamService.get_or_generate_exam(
        module_id=sanitized_module_id,
        num_questions=15,
        passing_score=70.0,
        time_limit=30
    )
    
    if not exam:
        raise HTTPException(status_code=404, detail="Examen non trouvé")
    
    # Vérifier si l'examen a un pdf_url directement
    pdf_url = exam.get("pdf_url")
    
    if not pdf_url:
        # Chercher la ressource PDF associée par titre (fallback)
        db = get_database()
        resource = await db.resources.find_one({
            "module_id": ObjectId(sanitized_module_id) if isinstance(sanitized_module_id, str) else sanitized_module_id,
            "resource_type": "pdf",
            "title": {"$regex": f"Examen.*", "$options": "i"}
        })
        
        if not resource or not resource.get("file_url"):
            # Si aucun PDF n'existe, essayer de le générer maintenant
            logger.info(f"PDF non trouvé pour l'examen, tentative de génération...")
            try:
                from app.services.pdf_generator_service import PDFGeneratorService
                from app.repositories.module_repository import ModuleRepository
                
                module = await ModuleRepository.find_by_id(sanitized_module_id)
                module_title = module.get("title", "Module") if module else "Module"
                
                pdf_path = await PDFGeneratorService._create_pdf_from_exam(
                    exam=exam,
                    module_title=module_title
                )
                
                if pdf_path and pdf_path.exists():
                    # Mettre à jour l'examen avec le nouveau PDF
                    pdf_url = f"/api/resources/files/{pdf_path.name}"
                    exam_id = exam.get('id') or exam.get('_id')
                    if exam_id:
                        await db.exams.update_one(
                            {"_id": ObjectId(str(exam_id))},
                            {"$set": {"pdf_url": pdf_url, "updated_at": datetime.now(timezone.utc)}}
                        )
                        logger.info(f"✅ PDF généré et mis à jour pour l'examen")
                else:
                    raise HTTPException(status_code=404, detail="Impossible de générer le PDF pour cet examen")
            except Exception as gen_error:
                logger.error(f"Erreur lors de la génération du PDF: {gen_error}", exc_info=True)
                raise HTTPException(status_code=404, detail=f"PDF non trouvé et impossible de le générer: {str(gen_error)}")
        else:
            pdf_url = resource.get("file_url")
    
    # Extraire le nom du fichier de l'URL
    # Normaliser le chemin (enlever les slashes et backslashes)
    filename = Path(pdf_url).name
    if not filename:
        # Si pdf_url est un chemin complet, extraire juste le nom
        filename = pdf_url.split("/")[-1].split("\\")[-1]
    
    from app.services.pdf_generator_service import PDF_DIR
    from app.routers.resources import UPLOAD_DIR
    import os
    
    # Normaliser tous les chemins en chemins absolus
    pdf_dir_abs = Path(PDF_DIR).resolve()
    upload_dir_abs = Path(UPLOAD_DIR).resolve() if UPLOAD_DIR else None
    
    # Essayer d'abord avec PDF_DIR (chemin absolu)
    file_path = pdf_dir_abs / filename
    if not file_path.exists():
        # Essayer avec UPLOAD_DIR
        if upload_dir_abs and upload_dir_abs.exists():
            file_path = upload_dir_abs / filename
            if not file_path.exists():
                # Essayer dans le sous-dossier resources
                file_path = upload_dir_abs / "resources" / filename
    
    if not file_path.exists():
        # Essayer avec le répertoire de travail actuel
        base_dir = Path(os.getcwd()).resolve()
        file_path = base_dir / "uploads" / "resources" / filename
        if not file_path.exists():
            # Dernier essai : chercher dans le backend/uploads/resources
            backend_dir = base_dir / "backend" / "uploads" / "resources"
            if backend_dir.exists():
                file_path = backend_dir / filename
    
    # Si le fichier n'existe toujours pas, régénérer le PDF
    if not file_path.exists():
        logger.warning(f"PDF non trouvé ({filename}), tentative de régénération...")
        try:
            from app.services.pdf_generator_service import PDFGeneratorService
            from app.repositories.module_repository import ModuleRepository
            
            module = await ModuleRepository.find_by_id(sanitized_module_id)
            module_title = module.get("title", "Module") if module else "Module"
            
            pdf_path = await PDFGeneratorService._create_pdf_from_exam(
                exam=exam,
                module_title=module_title
            )
            
            if pdf_path and pdf_path.exists():
                # Mettre à jour l'examen avec le nouveau PDF
                pdf_url = f"/api/resources/files/{pdf_path.name}"
                filename = pdf_path.name
                file_path = pdf_path
                
                db = get_database()
                exam_id = exam.get('id') or exam.get('_id')
                if exam_id:
                    await db.exams.update_one(
                        {"_id": ObjectId(str(exam_id))},
                        {"$set": {"pdf_url": pdf_url, "updated_at": datetime.now(timezone.utc)}}
                    )
                    logger.info(f"✅ PDF régénéré et mis à jour pour l'examen")
            else:
                raise Exception("Le PDF n'a pas pu être généré")
        except Exception as gen_error:
            logger.error(f"Erreur lors de la régénération du PDF: {gen_error}", exc_info=True)
            raise HTTPException(
                status_code=404, 
                detail=f"Fichier PDF non trouvé: {filename}. Impossible de régénérer le PDF. PDF_DIR: {pdf_dir_abs}"
            )
    
    # Récupérer le module pour le nom du fichier
    from app.repositories.module_repository import ModuleRepository
    module = await ModuleRepository.find_by_id(sanitized_module_id)
    module_title = module.get("title", "examen") if module else "examen"
    download_filename = f"Examen_{module_title}.pdf".replace(" ", "_")
    
    return FileResponse(
        path=str(file_path),
        filename=download_filename,
        media_type="application/pdf"
    )
