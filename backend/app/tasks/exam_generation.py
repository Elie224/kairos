"""
Tâches Celery pour la génération d'examens en arrière-plan
"""
from app.celery_app import celery_app
from app.services.exam_service import ExamService
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="generate_exam_async", bind=True, max_retries=3, default_retry_delay=30)
def generate_exam_async(self, module_id: str, user_id: str, num_questions: int = 10):
    """Génère un examen en arrière-plan"""
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            ExamService.generate_exam(module_id, user_id, num_questions)
        )
        logger.info(f"Examen généré avec succès pour module {module_id} par utilisateur {user_id}")
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la génération d'examen asynchrone: {e}", exc_info=True)
        # Retry avec exponential backoff
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
