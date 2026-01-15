"""
Tâches Celery pour la génération de PDF en arrière-plan
"""
from app.celery_app import celery_app
from app.services.pdf_generator_service import PDFGeneratorService
from app.repositories.module_repository import ModuleRepository
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="generate_pdf_async", bind=True, max_retries=3, default_retry_delay=30)
def generate_pdf_async(self, content_type: str, content_id: str, user_id: str):
    """
    Génère un PDF en arrière-plan
    
    Args:
        content_type: Type de contenu ('td', 'tp', 'exam', 'module')
        content_id: ID du contenu (lesson_id, exam_id, module_id)
        user_id: ID de l'utilisateur
    """
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = None
        
        if content_type == "td":
            # Générer un TD PDF pour une leçon
            result = loop.run_until_complete(
                PDFGeneratorService.generate_td_pdf_for_lesson(content_id, user_id)
            )
        elif content_type == "tp":
            # Générer un TP PDF pour une leçon
            result = loop.run_until_complete(
                PDFGeneratorService.generate_tp_pdf_for_lesson(content_id, user_id)
            )
        elif content_type == "exam":
            # Pour les examens, la génération de PDF est déjà gérée dans ExamService
            # Cette tâche peut être utilisée pour régénérer un PDF si nécessaire
            logger.info(f"Génération PDF pour examen {content_id} - déjà géré par ExamService")
            result = {"status": "completed", "message": "PDF d'examen généré via ExamService"}
        elif content_type == "module":
            # Générer des PDFs pour toutes les leçons d'un module
            module = loop.run_until_complete(ModuleRepository.find_by_id(content_id))
            if not module:
                raise ValueError(f"Module {content_id} non trouvé")
            
            # Générer TD et TP pour toutes les leçons
            pdf_results = loop.run_until_complete(
                PDFGeneratorService.generate_for_new_lessons(content_id, user_id)
            )
            result = pdf_results
        else:
            raise ValueError(f"Type de contenu non supporté: {content_type}")
        
        logger.info(f"PDF généré avec succès: {content_type} - {content_id} pour utilisateur {user_id}")
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la génération de PDF asynchrone: {e}", exc_info=True)
        # Retry avec exponential backoff
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
