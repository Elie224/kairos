"""
Routeur pour les modules d'apprentissage - Refactorisé avec services
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from app.models import Module, ModuleCreate, Subject, Difficulty
from app.services.module_service import ModuleService
from app.services.cached_module_service import CachedModuleService
from app.utils.security import InputSanitizer
from app.utils.permissions import require_admin, get_current_user
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_modules(
    subject: Optional[Subject] = Query(None),
    difficulty: Optional[Difficulty] = Query(None),
    search: Optional[str] = Query(None, description="Recherche dans le titre et la description"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> List[Dict[str, Any]]:
    """
    Récupère la liste des modules avec filtres optionnels et recherche.
    Retourne uniquement les modules avec des sujets valides (mathematics, computer_science).
    """
    try:
        # Sanitizer la recherche si fournie
        sanitized_search = None
        if search:
            sanitized_search = InputSanitizer.sanitize_string(search, max_length=100)
        
        # Essayer d'abord avec le cache, puis sans cache en cas d'erreur
        try:
            modules = await CachedModuleService.get_modules(
                subject=subject.value if subject else None,
                difficulty=difficulty.value if difficulty else None,
                search=sanitized_search,
                skip=skip,
                limit=limit
            )
        except Exception as cache_error:
            logger.warning(f"Erreur avec le cache, tentative sans cache: {cache_error}")
            # Essayer sans cache directement avec le service
            modules = await ModuleService.get_modules(
                subject=subject,
                difficulty=difficulty,
                search=sanitized_search,
                skip=skip,
                limit=limit
            )
        
        # Filtrer les modules pour ne garder que ceux avec des sujets valides
        # Optimisation: validation Pydantic seulement si nécessaire (éviter la validation complète pour chaque module)
        valid_modules = []
        valid_subjects = {"mathematics", "computer_science"}
        
        for module in (modules or []):
            try:
                if not isinstance(module, dict):
                    continue
                
                # Vérifier que le sujet est valide (filtre rapide)
                module_subject = module.get("subject")
                if not module_subject or module_subject not in valid_subjects:
                    logger.debug(f"Module ignoré: sujet '{module_subject}' non supporté (ID: {module.get('id', 'unknown')})")
                    continue
                
                # Validation légère: vérifier seulement les champs essentiels au lieu de la validation Pydantic complète
                # Cela améliore les performances pour les listes de modules
                required_fields = ["id", "title", "description", "subject"]
                if all(field in module and module[field] for field in required_fields):
                    # Ajouter le module directement sans validation Pydantic complète (plus rapide)
                    # La validation complète sera faite lors de l'accès individuel au module
                    valid_modules.append(module)
                else:
                    logger.warning(f"Module ignoré (champs manquants): {module.get('id', 'unknown')}")
                    continue
            except Exception as e:
                logger.warning(f"Erreur lors du traitement d'un module: {e} (ID: {module.get('id', 'unknown') if isinstance(module, dict) else 'unknown'})")
                continue
        
        logger.info(f"Retour de {len(valid_modules)} module(s) valide(s) sur {len(modules or [])} module(s) total(aux)")
        return valid_modules
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des modules: {e}", exc_info=True)
        # Retourner une liste vide en cas d'erreur plutôt qu'une erreur 500
        return []


@router.post("/", response_model=Module, status_code=201)
async def create_module(
    module_data: ModuleCreate,
    admin_user: dict = Depends(require_admin)
):
    """Crée un nouveau module (admin seulement)"""
    return await CachedModuleService.create_module(module_data)


# IMPORTANT: Les routes spécifiques doivent être définies AVANT les routes génériques
async def _perform_content_generation(module_id: str) -> Dict[str, Any]:
    """
    Tâche de fond pour la génération de contenu (TD, TP, Quiz)
    """
    from app.repositories.module_repository import ModuleRepository
    from app.services.pdf_generator_service import PDFGeneratorService
    from app.services.quiz_service import QuizService
    
    sanitized_id = module_id
    results = {
        "tds_generated": 0,
        "tps_generated": 0,
        "quiz_regenerated": False,
        "exam_generated": False,
        "errors": []
    }
    
    try:
        # Récupérer le module
        module = await ModuleRepository.find_by_id(sanitized_id)
        if not module:
            error_msg = f"Module {sanitized_id} non trouvé pour la génération de contenu."
            logger.error(error_msg)
            results["errors"].append({"type": "module_not_found", "error": error_msg})
            return results
        
        # Récupérer toutes les leçons
        content = module.get("content", {})
        lessons = content.get("lessons", [])
        
        logger.info(f"Module trouvé: {module.get('title', 'N/A')}")
        logger.info(f"Nombre de leçons trouvées: {len(lessons)}")
        
        # Filtrer et normaliser les leçons - être plus permissif
        valid_lessons = []
        for i, lesson in enumerate(lessons):
            # Vérifier plusieurs façons d'avoir un titre
            has_title = bool(
                lesson.get("title") or 
                lesson.get("name") or 
                lesson.get("heading") or
                (lesson.get("sections") and len(lesson.get("sections", [])) > 0 and lesson.get("sections", [])[0].get("heading"))
            )
            
            # Vérifier plusieurs façons d'avoir du contenu
            has_content = bool(
                lesson.get("content") or 
                lesson.get("sections") or
                lesson.get("description")
            )
            
            # Si la leçon a au moins un titre ou du contenu, elle est valide
            if has_title or has_content:
                valid_lessons.append(lesson)
                logger.info(f"Leçon {i+1} validée: titre={has_title}, contenu={has_content}")
            else:
                # Si la leçon est vide, créer une leçon minimale basée sur l'index
                logger.warning(f"Leçon {i+1} vide, création d'une leçon minimale")
                valid_lessons.append({
                    "title": f"Leçon {i+1}",
                    "content": f"Contenu de la leçon {i+1} du module {module.get('title', '')}",
                    "sections": []
                })
        
        lessons = valid_lessons
        
        # Si vraiment aucune leçon, créer une leçon par défaut basée sur le module
        if not lessons:
            logger.warning(f"Aucune leçon trouvée, création d'une leçon par défaut pour le module '{module.get('title', 'N/A')}'")
            lessons = [{
                "title": module.get("title", "Leçon principale"),
                "content": module.get("description", "") or f"Contenu du module {module.get('title', '')}",
                "sections": []
            }]
            logger.info(f"Leçon par défaut créée: {lessons[0]}")
        
        # Générer TD et TP pour toutes les leçons
        try:
            pdf_results = await PDFGeneratorService.generate_for_new_lessons(
                module_id=sanitized_id,
                new_lessons=lessons
            )
            results["tds_generated"] = len(pdf_results.get("tds", []))
            results["tps_generated"] = len(pdf_results.get("tps", []))
            results["errors"].extend(pdf_results.get("errors", []))
            logger.info(f"TD et TP générés: {results['tds_generated']} TD, {results['tps_generated']} TP")
        except Exception as e:
            logger.error(f"Erreur lors de la génération TD/TP: {e}", exc_info=True)
            results["errors"].append({"type": "td_tp_generation", "error": str(e)})
        
        # Régénérer le quiz (uniquement pour les modules d'informatique)
        try:
            # Vérifier d'abord si le module est d'informatique
            module_for_quiz = await ModuleRepository.find_by_id(sanitized_id)
            if module_for_quiz:
                module_subject = module_for_quiz.get("subject", "").lower()
                logger.info(f"Vérification quiz: module subject={module_subject}")
                if module_subject == "computer_science":
                    logger.info(f"🔄 Début de la génération du quiz pour le module {sanitized_id}")
                    try:
                        # Ajouter un timeout pour la génération du quiz (5 minutes pour permettre à OpenAI de répondre)
                        await asyncio.wait_for(
                            QuizService.regenerate_quiz(
                                module_id=sanitized_id,
                                num_questions=50,
                                difficulty=None
                            ),
                            timeout=300.0  # Timeout de 5 minutes pour la génération du quiz (OpenAI peut prendre du temps)
                        )
                        results["quiz_regenerated"] = True
                        logger.info("✅ Quiz régénéré avec succès")
                    except asyncio.TimeoutError:
                        error_msg = f"Timeout lors de la génération du quiz (dépassement de 5 minutes)"
                        logger.error(f"❌ {error_msg}")
                        results["errors"].append({"type": "quiz_regeneration_timeout", "error": error_msg})
                    except Exception as quiz_error:
                        error_msg = f"Erreur lors de la régénération du quiz: {str(quiz_error)}"
                        logger.error(f"❌ {error_msg}", exc_info=True)
                        results["errors"].append({"type": "quiz_regeneration", "error": error_msg})
                else:
                    logger.info(f"Quiz non généré pour le module de {module_subject} (uniquement pour informatique)")
            else:
                error_msg = "Module non trouvé pour la génération du quiz"
                logger.error(f"❌ {error_msg}")
                results["errors"].append({"type": "quiz_regeneration", "error": error_msg})
        except Exception as e:
            error_msg = f"Erreur lors de la régénération du quiz: {str(e)}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            results["errors"].append({"type": "quiz_regeneration", "error": error_msg})
        
        # Générer l'examen automatiquement pour tous les modules
        try:
            from app.services.exam_service import ExamService
            logger.info(f"🔄 Début de la génération de l'examen pour le module {sanitized_id}")
            await ExamService.get_or_generate_exam(
                module_id=sanitized_id,
                num_questions=15,
                passing_score=70.0,
                time_limit=30
            )
            results["exam_generated"] = True
            logger.info("✅ Examen généré avec succès")
        except Exception as exam_error:
            error_msg = f"Erreur lors de la génération de l'examen: {str(exam_error)}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            results["errors"].append({"type": "exam_generation", "error": error_msg})
        
        # Préparer le message de réponse
        message_parts = [f"Génération terminée pour {len(lessons)} leçon(s)"]
        if results["tds_generated"] > 0:
            message_parts.append(f"{results['tds_generated']} TD généré(s)")
        if results["tps_generated"] > 0:
            message_parts.append(f"{results['tps_generated']} TP généré(s)")
        if results["quiz_regenerated"]:
            message_parts.append("Quiz régénéré (50 questions)")
        if results.get("exam_generated"):
            message_parts.append("Examen généré")
        
        # Ajouter les erreurs au message si présentes
        if results["errors"]:
            error_messages = []
            for error in results["errors"]:
                if isinstance(error, dict):
                    error_type = error.get("type", "unknown")
                    error_msg = error.get("error", str(error))
                    lesson_name = error.get("lesson", "N/A")
                    error_messages.append(f"{error_type} pour '{lesson_name}': {error_msg}")
                else:
                    error_messages.append(str(error))
            message_parts.append(f"{len(results['errors'])} erreur(s): {'; '.join(error_messages[:3])}")  # Limiter à 3 erreurs pour la lisibilité
        
        # Vérifier si le client OpenAI est disponible
        from app.services.ai_service import client as openai_client
        if not openai_client:
            logger.error("Client OpenAI non initialisé - Vérifiez OPENAI_API_KEY dans .env")
            results["errors"].append({
                "type": "openai_client",
                "error": "Client OpenAI non initialisé. Vérifiez que OPENAI_API_KEY est configuré dans .env et redémarrez le backend."
            })
            message_parts.append("ERREUR: Client OpenAI non initialisé")
        
        # S'assurer que le message est toujours présent même s'il n'y a pas de résultats
        if not message_parts or len(message_parts) == 1:
            if results["tds_generated"] == 0 and results["tps_generated"] == 0:
                if not results["errors"]:
                    message_parts = [f"Aucun TD/TP généré pour {len(lessons)} leçon(s). Vérifiez que les leçons ont du contenu valide."]
                else:
                    message_parts = [f"Génération échouée pour {len(lessons)} leçon(s). {len(results['errors'])} erreur(s) détectée(s)."]
        
        logger.info(f"Fin de la tâche de fond de génération pour le module {sanitized_id}. Résultats: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Erreur inattendue dans la tâche de fond de génération: {e}", exc_info=True)
        results["errors"].append({"type": "unexpected_error", "error": str(e)})
        return results


@router.post("/{module_id}/generate-content", status_code=200)
async def generate_content_for_module(
    module_id: str,
    admin_user: dict = Depends(require_admin)
):
    """
    Force la génération automatique de quiz, TD et TP pour un module existant
    Utile pour régénérer le contenu après avoir ajouté des leçons manuellement
    Lance la génération en arrière-plan et retourne immédiatement
    """
    # Valider l'ObjectId
    sanitized_id = InputSanitizer.sanitize_object_id(module_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")
    
    try:
        # Vérifier que le module existe
        from app.repositories.module_repository import ModuleRepository
        module = await ModuleRepository.find_by_id(sanitized_id)
        if not module:
            raise HTTPException(status_code=404, detail="Module non trouvé")
        
        # Lancer la génération en tâche de fond pour ne pas bloquer le frontend
        asyncio.create_task(_perform_content_generation(sanitized_id))
        
        return {
            "message": "Génération de contenu lancée en arrière-plan. Veuillez rafraîchir la page dans quelques instants pour voir les mises à jour.",
            "tds_generated": 0,
            "tps_generated": 0,
            "quiz_regenerated": False,
            "errors": []
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la génération de contenu: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")


@router.get("/{module_id}", response_model=Module)
async def get_module(module_id: str):
    """Récupère un module spécifique"""
    # Valider l'ObjectId
    sanitized_id = InputSanitizer.sanitize_object_id(module_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")
    
    # Utiliser le service avec cache
    return await CachedModuleService.get_module(sanitized_id)


@router.put("/{module_id}", response_model=Module)
async def update_module(
    module_id: str,
    update_data: ModuleCreate,  # Utiliser ModuleCreate pour validation complète
    admin_user: dict = Depends(require_admin)
):
    """Met à jour un module (admin seulement)"""
    # Valider l'ObjectId
    sanitized_id = InputSanitizer.sanitize_object_id(module_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")
    
    # Convertir le Pydantic model en dict pour le service
    update_dict = update_data.dict(exclude_unset=True)
    return await CachedModuleService.update_module(sanitized_id, update_dict)


@router.delete("/{module_id}", status_code=204)
async def delete_module(
    module_id: str,
    admin_user: dict = Depends(require_admin)
):
    """Supprime un module (admin seulement)"""
    # Valider l'ObjectId
    sanitized_id = InputSanitizer.sanitize_object_id(module_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")
    
    await CachedModuleService.delete_module(sanitized_id)
    return None
