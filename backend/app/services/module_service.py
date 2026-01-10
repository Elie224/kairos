"""
Service pour la gestion des modules - Business logic
"""
from typing import List, Dict, Any, Optional
from app.repositories.module_repository import ModuleRepository
from app.models import ModuleCreate, Subject, Difficulty
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ModuleService:
    """Service pour la gestion des modules"""
    
    @staticmethod
    async def get_modules(
        subject: Optional[Subject] = None,
        difficulty: Optional[Difficulty] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Récupère les modules avec filtres et recherche"""
        try:
            result = await ModuleRepository.find_all(subject, difficulty, search, skip, limit)
            return result or []
        except Exception as e:
            logger.error(f"Erreur dans ModuleService.get_modules: {e}", exc_info=True)
            # Retourner une liste vide en cas d'erreur
            return []
    
    @staticmethod
    async def get_module(module_id: str) -> Dict[str, Any]:
        """Récupère un module par ID"""
        module = await ModuleRepository.find_by_id(module_id)
        if not module:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Module non trouvé")
        return module
    
    @staticmethod
    async def create_module(module_data: ModuleCreate) -> Dict[str, Any]:
        """Crée un nouveau module"""
        # Limiter la taille du contenu du module pour éviter des documents MongoDB trop volumineux
        import json
        content_str = json.dumps(module_data.content or {})
        max_content_size = 200_000  # 200 KB
        if len(content_str.encode('utf-8')) > max_content_size:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le contenu du module est trop volumineux (max 200 KB)"
            )
        from datetime import timezone
        module_dict = {
            **module_data.dict(),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        module = await ModuleRepository.create(module_dict)
        
        # Générer automatiquement TD, TP, quiz et examen en arrière-plan pour ne pas bloquer la création
        # La création du module retourne immédiatement, la génération se fait en tâche de fond
        content = module_data.content or {}
        lessons = content.get("lessons", [])
        if lessons:
            import asyncio
            
            async def generate_content_background():
                """Tâche de fond pour générer le contenu (TD, TP, Quiz, Examen)"""
                try:
                    module_id = module.get("id", "")
                    logger.info(f"🔄 Début de la génération de contenu en arrière-plan pour le module {module_id}")
                    
                    # Générer TD et TP en PDF
                    from app.services.pdf_generator_service import PDFGeneratorService
                    pdf_results = await PDFGeneratorService.generate_for_new_lessons(
                        module_id=module_id,
                        new_lessons=lessons
                    )
                    logger.info(f"✅ TD et TP générés automatiquement pour {len(lessons)} leçon(s)")
                    logger.info(f"Résultats: {len(pdf_results.get('tds', []))} TD, {len(pdf_results.get('tps', []))} TP générés")
                    
                    # Générer le quiz initial uniquement pour les modules d'informatique
                    try:
                        module_subject = module.get("subject", "").lower()
                        if module_subject == "computer_science":
                            from app.services.quiz_service import QuizService
                            await QuizService.get_or_generate_quiz(
                                module_id=module_id,
                                num_questions=50,
                                difficulty=None,
                                force_regenerate=False
                            )
                            logger.info(f"✅ Quiz généré automatiquement pour le module d'informatique")
                    except Exception as quiz_error:
                        logger.error(f"❌ Erreur lors de la génération du quiz: {quiz_error}", exc_info=True)
                    
                    # Générer l'examen automatiquement pour tous les modules
                    try:
                        from app.services.exam_service import ExamService
                        await ExamService.get_or_generate_exam(
                            module_id=module_id,
                            num_questions=15,
                            passing_score=70.0,
                            time_limit=30
                        )
                        logger.info(f"✅ Examen généré automatiquement")
                    except Exception as exam_error:
                        logger.error(f"❌ Erreur lors de la génération de l'examen: {exam_error}", exc_info=True)
                    
                    logger.info(f"✅ Génération de contenu terminée pour le module {module_id}")
                except Exception as e:
                    logger.error(f"❌ Erreur lors de la génération automatique de contenu: {e}", exc_info=True)
            
            # Lancer la génération en arrière-plan
            asyncio.create_task(generate_content_background())
            logger.info(f"📝 Module créé avec succès. Génération de contenu lancée en arrière-plan.")
        
        return module
    
    @staticmethod
    async def update_module(module_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Met à jour un module"""
        # Validate content size if provided
        import json
        if update_data.get("content") is not None:
            content_str = json.dumps(update_data.get("content", {}))
            max_content_size = 200_000  # 200 KB
            if len(content_str.encode('utf-8')) > max_content_size:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Le contenu du module est trop volumineux (max 200 KB)"
                )
        
        # Sauvegarder l'ancien module pour détecter les nouvelles leçons
        old_module = await ModuleRepository.find_by_id(module_id)
        old_lessons = []
        if old_module:
            old_content = old_module.get("content", {})
            old_lessons = old_content.get("lessons", [])
        
        # Mettre à jour le module
        from datetime import timezone
        update_data["updated_at"] = datetime.now(timezone.utc)
        module = await ModuleRepository.update(module_id, update_data)
        if not module:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Module non trouvé")
        
        # Détecter les nouvelles leçons APRÈS la mise à jour
        new_lessons = []
        new_content = module.get("content", {})
        new_lessons_list = new_content.get("lessons", [])
        
        if old_module and new_lessons_list:
            # Identifier les nouvelles leçons (par titre)
            old_titles = {lesson.get("title", "") for lesson in old_lessons if lesson.get("title")}
            new_lessons = [
                lesson for lesson in new_lessons_list
                if lesson.get("title", "") and lesson.get("title", "") not in old_titles
            ]
            logger.info(f"Détection de nouvelles leçons: {len(new_lessons)} nouvelle(s) leçon(s) détectée(s) sur {len(new_lessons_list)} total")
        elif not old_module and new_lessons_list:
            # Si c'est la première fois qu'on ajoute des leçons (module créé sans leçons puis mis à jour)
            new_lessons = new_lessons_list
            logger.info(f"Première détection de leçons: {len(new_lessons)} leçon(s) détectée(s)")
        elif new_lessons_list and not old_lessons:
            # Cas où le module n'avait pas de leçons avant
            new_lessons = new_lessons_list
            logger.info(f"Ajout de leçons à un module sans leçons: {len(new_lessons)} leçon(s) ajoutée(s)")
        
        # Générer automatiquement TD, TP et régénérer le quiz pour les nouvelles leçons
        if new_lessons:
            try:
                # Générer TD et TP en PDF
                from app.services.pdf_generator_service import PDFGeneratorService
                pdf_results = await PDFGeneratorService.generate_for_new_lessons(
                    module_id=module_id,
                    new_lessons=new_lessons
                )
                logger.info(f"TD et TP générés automatiquement pour {len(new_lessons)} nouvelle(s) leçon(s)")
                logger.info(f"Résultats: {len(pdf_results.get('tds', []))} TD, {len(pdf_results.get('tps', []))} TP générés")
                
                # Régénérer le quiz pour inclure les nouvelles leçons
                try:
                    from app.services.quiz_service import QuizService
                    await QuizService.regenerate_quiz(
                        module_id=module_id,
                        num_questions=40,
                        difficulty=None
                    )
                    logger.info(f"Quiz régénéré automatiquement pour inclure les nouvelles leçons")
                except Exception as quiz_error:
                    logger.error(f"Erreur lors de la régénération du quiz: {quiz_error}", exc_info=True)
                    # Ne pas faire échouer si le quiz ne peut pas être régénéré
                    
            except Exception as e:
                logger.error(f"Erreur lors de la génération automatique de TD/TP: {e}", exc_info=True)
                # Ne pas faire échouer la mise à jour du module si la génération échoue
        
        return module
    
    @staticmethod
    async def delete_module(module_id: str) -> bool:
        """Supprime un module"""
        return await ModuleRepository.delete(module_id)
    
    @staticmethod
    async def get_modules_by_subject(subject: Subject) -> List[Dict[str, Any]]:
        """Récupère tous les modules d'une matière"""
        return await ModuleRepository.find_by_subject(subject)
    
    @staticmethod
    async def get_module_count(subject: Optional[Subject] = None) -> int:
        """Compte le nombre de modules"""
        return await ModuleRepository.count(subject)


