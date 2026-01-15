"""
Service pour la gestion des examens - Business logic
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from app.repositories.exam_repository import ExamRepository, ExamAttemptRepository
from app.repositories.module_repository import ModuleRepository
from app.repositories.progress_repository import ProgressRepository
from app.repositories.quiz_repository import QuizRepository
from app.services.ai_service import AIService
from app.models import ExamCreate, ExamQuestion, ExamSubmission, ExamAnswer
from fastapi import HTTPException
import logging
import asyncio

logger = logging.getLogger(__name__)


class ExamService:
    """Service pour la gestion des examens"""

    @staticmethod
    async def check_prerequisites(user_id: str, module_id: str) -> Dict[str, Any]:
        """
        Vérifie que l'étudiant peut passer l'examen :
        - Pour les modules avec quiz : doit avoir réussi 90% du quiz
        - Pour les modules sans quiz : accès direct à l'examen (avec les TDs)
        """
        try:
            from app.repositories.quiz_repository import QuizRepository
            
            # Vérifier que le module existe
            module = await ModuleRepository.find_by_id(module_id)
            if not module:
                return {
                    "can_take_exam": False,
                    "reason": "Module non trouvé",
                    "module_completed": False,
                    "quiz_completed": False,
                    "quiz_score": None
                }

            # Vérifier si le module a un quiz (seulement pour computer_science)
            module_subject = module.get("subject", "").lower()
            has_quiz = module_subject == "computer_science"
            
            if has_quiz:
                # Pour les modules avec quiz : vérifier que l'utilisateur a réussi 90% du quiz
                quiz = await QuizRepository.find_by_module_id(module_id)
                if not quiz:
                    return {
                        "can_take_exam": False,
                        "reason": "Le quiz n'est pas encore disponible pour ce module",
                        "module_completed": False,
                        "quiz_completed": False,
                        "quiz_score": None
                    }
                
                # Récupérer les tentatives de quiz de l'utilisateur
                attempts = await QuizRepository.find_attempts_by_user_and_module(user_id, module_id)
                if not attempts:
                    return {
                        "can_take_exam": False,
                        "reason": "Vous devez compléter le quiz avec au moins 90% de réussite avant de passer l'examen",
                        "module_completed": False,
                        "quiz_completed": False,
                        "quiz_score": None
                    }
                
                # Prendre la meilleure tentative
                best_attempt = max(attempts, key=lambda a: a.get("percentage", 0))
                quiz_score = best_attempt.get("percentage", 0)
                
                # Vérifier que le score est >= 90%
                can_take_exam = quiz_score >= 90.0
                
                return {
                    "can_take_exam": can_take_exam,
                    "reason": "Prérequis satisfaits" if can_take_exam else f"Vous devez obtenir au moins 90% au quiz pour passer l'examen. Votre meilleur score : {quiz_score:.1f}%",
                    "module_completed": True,  # Considéré comme complété si le quiz est fait
                    "quiz_completed": True,
                    "quiz_score": quiz_score,
                    "required_score": 90.0
                }
            else:
                # Pour les modules sans quiz (mathématiques) : accès direct à l'examen à tout moment
                # Les examens de mathématiques sont toujours disponibles car ils n'ont pas besoin de QCM
                progress = await ProgressRepository.find_by_user_and_module(user_id, module_id)
                module_completed = progress and progress.get("completed", False)
                
                return {
                    "can_take_exam": True,  # Toujours accessible pour les mathématiques
                    "reason": "Prérequis satisfaits - Les examens de mathématiques sont disponibles à tout moment",
                    "module_completed": module_completed,
                    "quiz_completed": None,  # Pas de quiz pour ce module
                    "quiz_score": None,
                    "has_quiz": False
                }
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des prérequis: {e}")
            raise

    @staticmethod
    async def get_or_generate_exam(
        module_id: str,
        num_questions: int = 15,
        passing_score: float = 70.0,
        time_limit: int = 30,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Récupère l'examen d'un module ou le génère s'il n'existe pas
        """
        try:
            # Vérifier si un examen existe déjà pour ce module
            existing_exam = await ExamRepository.find_by_module_id(module_id)
            if existing_exam and not force_regenerate:
                # Vérifier si c'est un module de mathématiques et si l'examen a la nouvelle structure
                module = await ModuleRepository.find_by_id(module_id)
                module_subject = module.get("subject", "").lower() if module else ""
                is_mathematics = module_subject == "mathematics"
                
                # Vérifier si l'examen doit être régénéré
                needs_regeneration = False
                
                if is_mathematics:
                    # Pour les mathématiques, vérifier plusieurs conditions :
                    # 1. L'examen n'a pas le type "mathematics"
                    # 2. L'examen n'a pas d'exercices pratiques
                    # 3. Les exercices pratiques n'ont pas la nouvelle structure (parts + subquestions)
                    practical_exercises = existing_exam.get("practical_exercises", [])
                    
                    if existing_exam.get("exam_type") != "mathematics":
                        needs_regeneration = True
                        logger.info(f"Examen existant pour module mathématiques sans type 'mathematics', régénération...")
                    elif not practical_exercises or len(practical_exercises) == 0:
                        needs_regeneration = True
                        logger.info(f"Examen existant pour module mathématiques sans exercices pratiques, régénération...")
                    else:
                        # Vérifier si les exercices ont la nouvelle structure avec parts et subquestions
                        has_new_structure = False
                        for exercise in practical_exercises:
                            if "parts" in exercise and exercise.get("parts"):
                                for part in exercise.get("parts", []):
                                    if "subquestions" in part and part.get("subquestions"):
                                        has_new_structure = True
                                        break
                                if has_new_structure:
                                    break
                        
                        if not has_new_structure:
                            needs_regeneration = True
                            logger.info(f"Examen existant pour module mathématiques avec ancienne structure, régénération avec nouvelle structure...")
                
                if needs_regeneration:
                    # Supprimer l'ancien examen pour en créer un nouveau
                    from app.database import get_database
                    from bson import ObjectId
                    db = get_database()
                    exam_id = existing_exam.get('id') or existing_exam.get('_id')
                    if exam_id:
                        logger.info(f"Suppression de l'ancien examen (ID: {exam_id}) pour régénération...")
                        await db.exams.delete_one({"_id": ObjectId(str(exam_id))})
                        # Supprimer aussi les tentatives associées si nécessaire
                        await db.exam_attempts.delete_many({"exam_id": str(exam_id)})
                    # Continuer pour générer un nouvel examen
                else:
                    logger.info(f"Examen existant trouvé pour le module {module_id}")
                    return existing_exam

            # Vérifier que le module existe
            module = await ModuleRepository.find_by_id(module_id)
            if not module:
                raise HTTPException(
                    status_code=404,
                    detail=f"Module non trouvé"
                )

            # Vérifier si c'est un module de mathématiques
            module_subject = module.get("subject", "").lower()
            is_mathematics = module_subject == "mathematics"
            
            # Générer l'examen via l'IA en utilisant le contenu du module
            logger.info(f"Génération d'un nouvel examen pour le module {module_id} (type: {'mathematics' if is_mathematics else 'standard'})")
            
            from bson import ObjectId
            exam_data = {
                "module_id": ObjectId(module_id) if isinstance(module_id, str) else module_id,
                "passing_score": passing_score,
                "time_limit": time_limit,
                "created_at": datetime.now(timezone.utc)
            }
            
            if is_mathematics:
                # Pour les mathématiques : générer deux parties
                # Partie 1 : QCM (25% de la note) - environ 5-8 questions
                num_qcm_questions = max(5, int(num_questions * 0.3))  # 30% du total pour le QCM
                logger.info(f"Génération de {num_qcm_questions} questions QCM (25% de la note)")
                
                ai_qcm = await AIService.generate_exam_questions(
                    module_id=module_id,
                    num_questions=num_qcm_questions,
                    difficulty=None
                )
                
                exam_questions = []
                for q in ai_qcm.get("questions", []):
                    exam_questions.append({
                        "question": q.get("question", ""),
                        "options": q.get("options", []),
                        "correct_answer": q.get("correct_answer", 0),
                        "explanation": q.get("explanation", ""),
                        "points": 1.0
                    })
                
                if len(exam_questions) < 3:
                    raise HTTPException(
                        status_code=500,
                        detail="Impossible de générer suffisamment de questions QCM pour l'examen"
                    )
                
                # Partie 2 : Exercices pratiques (75% de la note) - générés via l'IA
                logger.info("Génération des exercices pratiques (75% de la note)")
                practical_exercises = await ExamService._generate_practical_exercises(
                    module_id=module_id,
                    module=module
                )
                
                if not practical_exercises or len(practical_exercises) < 2:
                    raise HTTPException(
                        status_code=500,
                        detail="Impossible de générer suffisamment d'exercices pratiques structurés pour l'examen. Veuillez réessayer."
                    )
                
                # Compter le nombre total de sous-questions pour validation
                total_subquestions = 0
                for exercise in practical_exercises:
                    if "parts" in exercise:
                        for part in exercise.get("parts", []):
                            total_subquestions += len(part.get("subquestions", []))
                    else:
                        total_subquestions += 1  # Ancien format
                
                logger.info(f"✅ {len(practical_exercises)} exercices structurés générés avec {total_subquestions} sous-questions au total")
                
                exam_data.update({
                    "exam_type": "mathematics",
                    "questions": exam_questions,
                    "num_questions": len(exam_questions),
                    "practical_exercises": practical_exercises,
                    "qcm_weight": 0.25,
                    "practical_weight": 0.75
                })
            else:
                # Pour les autres modules : examen standard avec QCM uniquement
                ai_exam = await AIService.generate_exam_questions(
                    module_id=module_id,
                    num_questions=num_questions,
                    difficulty=None
                )

                exam_questions = []
                for q in ai_exam.get("questions", []):
                    exam_questions.append({
                        "question": q.get("question", ""),
                        "options": q.get("options", []),
                        "correct_answer": q.get("correct_answer", 0),
                        "explanation": q.get("explanation", ""),
                        "points": 1.0
                    })

                if len(exam_questions) < 5:
                    raise HTTPException(
                        status_code=500,
                        detail="Impossible de générer suffisamment de questions pour l'examen"
                    )
                
                exam_data.update({
                    "exam_type": "standard",
                    "questions": exam_questions,
                    "num_questions": len(exam_questions),
                    "qcm_weight": 1.0,
                    "practical_weight": 0.0
                })

            exam = await ExamRepository.create(exam_data)
            
            # Générer le PDF de l'examen
            try:
                from app.services.pdf_generator_service import PDFGeneratorService
                from app.repositories.resource_repository import ResourceRepository
                from app.models import ResourceCreate, ResourceType
                from app.database import get_database
                from bson import ObjectId
                
                module = await ModuleRepository.find_by_id(module_id)
                module_title = module.get("title", "Module") if module else "Module"
                module_subject = module.get("subject", "").lower() if module else ""
                
                # Pour les examens de mathématiques, s'assurer que les exercices pratiques sont inclus
                if module_subject == "mathematics" and exam.get("exam_type") == "mathematics":
                    # Le PDF inclura automatiquement les exercices pratiques
                    logger.info("Génération du PDF avec exercices pratiques pour l'examen de mathématiques")
                
                pdf_path = await PDFGeneratorService._create_pdf_from_exam(
                    exam=exam,
                    module_title=module_title
                )
                
                if pdf_path:
                    # Sauvegarder le PDF comme ressource
                    resource_data = ResourceCreate(
                        module_id=module_id,
                        title=f"Examen - {module_title}",
                        description=f"Examen en PDF pour le module : {module_title}",
                        resource_type=ResourceType.PDF,
                        file_url=f"/api/resources/files/{pdf_path.name}",
                        file_size=pdf_path.stat().st_size,
                        file_name=pdf_path.name
                    )
                    
                    resource_dict = resource_data.dict()
                    resource_dict["created_at"] = datetime.now(timezone.utc)
                    resource_dict["updated_at"] = datetime.now(timezone.utc)
                    resource = await ResourceRepository.create(resource_dict)
                    
                    # Mettre à jour l'examen avec l'URL du PDF
                    pdf_url = f"/api/resources/files/{pdf_path.name}"
                    db = get_database()
                    exam_id = exam.get('id') or exam.get('_id')
                    if exam_id and isinstance(exam, dict):
                        await db.exams.update_one(
                            {"_id": ObjectId(str(exam_id))},
                            {"$set": {"pdf_url": pdf_url, "updated_at": datetime.now(timezone.utc)}}
                        )
                        exam["pdf_url"] = pdf_url
                        logger.info(f"✅ Examen mis à jour avec pdf_url: {pdf_url}")
                    else:
                        logger.warning(f"⚠️ Impossible de mettre à jour l'examen: exam_id={exam_id}, exam_type={type(exam)}")
                    
                    logger.info(f"✅ PDF Examen généré et sauvegardé pour le module {module_id}")
            except Exception as pdf_error:
                logger.error(f"Erreur lors de la génération du PDF de l'examen: {pdf_error}", exc_info=True)
                # Ne pas faire échouer la création de l'examen si le PDF ne peut pas être généré
            
            return exam

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la récupération/génération de l'examen: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de la génération de l'examen: {str(e)}"
            )
    
    @staticmethod
    async def _generate_practical_exercises(module_id: str, module: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Génère des exercices pratiques pour les examens de mathématiques (75% de la note)
        """
        try:
            # Récupérer le contenu complet du module
            module_title = module.get("title", "")
            module_description = module.get("description", "")
            lessons = module.get("lessons", [])
            difficulty = module.get("difficulty", "intermediate")
            
            # Construire le contexte du module
            module_context = f"Module: {module_title}\nDescription: {module_description}\n"
            
            if lessons:
                module_context += "\nLeçons du module:\n"
                for lesson in lessons[:10]:  # Limiter à 10 leçons pour le contexte
                    lesson_title = lesson.get("title", "")
                    lesson_content = lesson.get("content", "")[:500]  # Limiter la longueur
                    module_context += f"- {lesson_title}: {lesson_content}\n"
            
            # Générer 3-5 exercices structurés de niveau examen national
            import json
            from app.services.ai_service import client, AI_MODEL
            
            prompt = f"""Tu es un PROFESSEUR DE MATHÉMATIQUES EXPERT qui compose des examens de niveau NATIONAL.

{module_context}

TON RÔLE :
Tu es un professeur de mathématiques expérimenté qui compose des examens officiels de niveau national. 
Tu dois créer des exercices SOLIDES, STRUCTURÉS et PROFESSIONNELS comme dans un vrai examen national.

STRUCTURE REQUISE POUR CHAQUE EXERCICE :
Chaque exercice doit être composé comme un exercice d'examen national :
- Un ENONCÉ principal complet et détaillé
- Plusieurs PARTIES (Partie A, Partie B, Partie C, etc.) qui se complètent
- Chaque partie doit avoir plusieurs SOUS-QUESTIONS (a, b, c, etc.)
- Les sous-questions doivent être progressives et logiques
- Les parties doivent s'enchaîner de manière cohérente

EXEMPLE DE STRUCTURE :
Exercice 1 : [Titre ou contexte de l'exercice]
Partie A : [Première partie de l'exercice]
  a) [Première sous-question]
  b) [Deuxième sous-question]
  c) [Troisième sous-question]
Partie B : [Deuxième partie qui utilise les résultats de la Partie A]
  a) [Sous-question]
  b) [Sous-question]
Partie C : [Troisième partie, plus avancée]
  a) [Sous-question complexe]
  b) [Sous-question complexe]

INSTRUCTIONS STRICTES :
- Génère 3 à 5 exercices MAJEURS (pas 8-12 petits exercices)
- Chaque exercice doit être SUBSTANTIEL et COMPLET (comme dans un examen national)
- Chaque exercice doit avoir 2 à 4 PARTIES (Partie A, B, C, D)
- Chaque partie doit avoir 2 à 4 SOUS-QUESTIONS (a, b, c, d)
- Les exercices doivent être de niveau PROFESSIONNEL et EXIGEANT
- Les exercices doivent tester la COMPRÉHENSION APPROFONDIE et la RÉSOLUTION DE PROBLÈMES
- Les exercices doivent être PROGRESSIFS (du moyen au très avancé)
- Adapte la difficulté au niveau du module ({difficulty}) mais reste EXIGEANT
- Les exercices doivent être des CAS RÉELS et CONCRETS, pas des exercices théoriques basiques

FORMAT DE RÉPONSE JSON strict :
{{
  "exercises": [
    {{
      "title": "<Titre ou contexte de l'exercice (ex: 'Étude d'une fonction', 'Problème de géométrie', etc.)'>",
      "parts": [
        {{
          "part_label": "Partie A",
          "part_title": "<Titre ou description de la partie>",
          "subquestions": [
            {{
              "label": "a)",
              "question": "<Énoncé de la sous-question a)>"
            }},
            {{
              "label": "b)",
              "question": "<Énoncé de la sous-question b)>"
            }},
            {{
              "label": "c)",
              "question": "<Énoncé de la sous-question c)>"
            }}
          ]
        }},
        {{
          "part_label": "Partie B",
          "part_title": "<Titre ou description de la partie>",
          "subquestions": [
            {{
              "label": "a)",
              "question": "<Énoncé de la sous-question a)>"
            }},
            {{
              "label": "b)",
              "question": "<Énoncé de la sous-question b)>"
            }}
          ]
        }}
      ],
      "difficulty": "{difficulty}",
      "estimated_time": 30
    }},
    ...
  ]
}}

IMPORTANT :
- Génère des exercices de QUALITÉ PROFESSIONNELLE comme dans un examen national
- Chaque exercice doit être COMPLET et SUBSTANTIEL
- Structure claire avec parties et sous-questions
- Pas d'exercices basiques ou trop simples
- Niveau EXIGEANT et PROFESSIONNEL
- Génère exactement 3 à 5 exercices MAJEURS au format JSON ci-dessus."""

            # client.chat.completions.create() est synchrone, utiliser asyncio.to_thread
            from app.services.ai_service import _get_max_tokens_param
            create_params = {
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": "Tu es un PROFESSEUR DE MATHÉMATIQUES EXPERT qui compose des examens de niveau NATIONAL. Tu crées des exercices SOLIDES, STRUCTURÉS et PROFESSIONNELS avec des parties et sous-questions, comme dans un vrai examen national."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.6,  # Légèrement plus bas pour plus de cohérence
            }
            # Utiliser _get_max_tokens_param pour gérer max_tokens vs max_completion_tokens
            create_params.update(_get_max_tokens_param(AI_MODEL, 6000))
            response = await asyncio.to_thread(client.chat.completions.create, **create_params)
            
            content = response.choices[0].message.content.strip()
            
            # Nettoyer le contenu JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Parser le JSON
            from app.utils.json_cleaner import safe_json_loads
            exercises_data = safe_json_loads(content)
            
            if not exercises_data or "exercises" not in exercises_data:
                logger.error("Format de réponse invalide pour les exercices pratiques")
                return []
            
            exercises = exercises_data.get("exercises", [])
            
            # Valider la structure des exercices
            validated_exercises = []
            for exercise in exercises:
                if "parts" in exercise and exercise.get("parts"):
                    # Vérifier que chaque partie a des sous-questions
                    valid_parts = []
                    for part in exercise.get("parts", []):
                        if "subquestions" in part and part.get("subquestions"):
                            valid_parts.append(part)
                    if valid_parts:
                        exercise["parts"] = valid_parts
                        validated_exercises.append(exercise)
                elif "question" in exercise:
                    # Format ancien : convertir en nouveau format
                    validated_exercises.append({
                        "title": exercise.get("title", "Exercice"),
                        "parts": [{
                            "part_label": "Partie A",
                            "part_title": "",
                            "subquestions": [{
                                "label": "a)",
                                "question": exercise.get("question", "")
                            }]
                        }],
                        "difficulty": exercise.get("difficulty", difficulty),
                        "estimated_time": exercise.get("estimated_time", 20)
                    })
            
            if not validated_exercises:
                logger.error("Aucun exercice valide généré")
                return []
            
            logger.info(f"✅ {len(validated_exercises)} exercices structurés générés pour l'examen de mathématiques (niveau national)")
            
            return validated_exercises
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des exercices pratiques: {e}", exc_info=True)
            return []

    @staticmethod
    async def start_exam_attempt(user_id: str, exam_id: str) -> Dict[str, Any]:
        """
        Démarre une tentative d'examen
        """
        try:
            # Récupérer l'examen
            exam = await ExamRepository.find_by_id(exam_id)
            if not exam:
                raise HTTPException(status_code=404, detail="Examen non trouvé")

            module_id = exam.get("module_id")

            # Vérifier les prérequis
            prerequisites = await ExamService.check_prerequisites(user_id, module_id)
            if not prerequisites.get("can_take_exam"):
                raise HTTPException(
                    status_code=403,
                    detail=prerequisites.get("reason", "Prérequis non satisfaits")
                )

            # Créer la tentative
            # S'assurer que module_id est une string (peut être ObjectId depuis MongoDB)
            module_id_str = str(module_id) if module_id else None
            exam_id_str = str(exam_id) if exam_id else None
            
            attempt_data = {
                "user_id": user_id,
                "exam_id": exam_id_str,
                "module_id": module_id_str,
                "score": 0.0,
                "max_score": float(len(exam.get("questions", []))),
                "percentage": 0.0,
                "passed": False,
                "answers": [],
                "time_spent": 0,
                "started_at": datetime.now(timezone.utc)
            }

            attempt = await ExamAttemptRepository.create(attempt_data)
            return attempt

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur lors du démarrage de la tentative: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors du démarrage de la tentative: {str(e)}"
            )

    @staticmethod
    async def submit_exam(
        user_id: str,
        submission: ExamSubmission
    ) -> Dict[str, Any]:
        """
        Soumet les réponses d'un examen et calcule le score
        """
        try:
            # Récupérer l'examen
            exam = await ExamRepository.find_by_id(submission.exam_id)
            if not exam:
                raise HTTPException(status_code=404, detail="Examen non trouvé")

            questions = exam.get("questions", [])
            passing_score = exam.get("passing_score", 70.0)
            module_id = exam.get("module_id")
            exam_type = exam.get("exam_type", "standard")
            qcm_weight = exam.get("qcm_weight", 1.0)
            practical_weight = exam.get("practical_weight", 0.0)

            # Calculer le score de la partie QCM
            qcm_score = 0.0
            qcm_max_score = 0.0
            answers_detail = []

            for answer in submission.answers:
                question_index = answer.question_index
                if question_index < len(questions):
                    question = questions[question_index]
                    points = question.get("points", 1.0)
                    qcm_max_score += points

                    if answer.answer == question.get("correct_answer", -1):
                        qcm_score += points
                        answers_detail.append({
                            "question_index": question_index,
                            "answer": answer.answer,
                            "correct": True,
                            "points": points
                        })
                    else:
                        answers_detail.append({
                            "question_index": question_index,
                            "answer": answer.answer,
                            "correct": False,
                            "points": 0.0,
                            "correct_answer": question.get("correct_answer")
                        })

            # Pour les examens de mathématiques, calculer aussi le score pratique
            practical_score = 0.0
            practical_max_score = 0.0
            practical_answers = []
            
            if exam_type == "mathematics" and practical_weight > 0:
                # Récupérer les réponses pratiques depuis submission
                # Note: Les exercices pratiques seront corrigés manuellement par l'enseignant
                # Pour l'instant, on stocke les réponses mais on ne calcule pas automatiquement
                practical_exercises = exam.get("practical_exercises", [])
                practical_max_score = len(practical_exercises) * 10.0  # 10 points par exercice
                
                # Les réponses pratiques sont stockées dans submission.practical_answers si disponibles
                if submission.practical_answers:
                    # Stocker les réponses pour correction manuelle ultérieure
                    practical_answers = submission.practical_answers
                    # Pour l'instant, score = 0 (sera corrigé manuellement par l'enseignant)
                    practical_score = 0.0
                else:
                    # Pas de réponses pratiques soumises, score = 0
                    practical_score = 0.0
                    practical_max_score = len(practical_exercises) * 10.0
            
            # Calculer le score total pondéré
            if exam_type == "mathematics":
                # Score QCM (25%) + Score Pratique (75%)
                qcm_percentage = (qcm_score / qcm_max_score * 100) if qcm_max_score > 0 else 0.0
                practical_percentage = (practical_score / practical_max_score * 100) if practical_max_score > 0 else 0.0
                
                total_score = (qcm_percentage * qcm_weight) + (practical_percentage * practical_weight)
                max_score = 100.0  # Score total sur 100
                percentage = total_score
            else:
                # Examen standard : uniquement QCM
                total_score = qcm_score
                max_score = qcm_max_score
                percentage = (total_score / max_score * 100) if max_score > 0 else 0.0
            
            passed = percentage >= passing_score

            # Trouver la tentative la plus récente pour cet examen et cet utilisateur
            attempts = await ExamAttemptRepository.find_by_user_and_exam(user_id, submission.exam_id)
            if not attempts:
                raise HTTPException(
                    status_code=404,
                    detail="Tentative d'examen non trouvée. Veuillez démarrer une tentative d'abord."
                )

            # Prendre la tentative la plus récente qui n'est pas encore complétée
            latest_attempt = None
            for attempt in attempts:
                if not attempt.get("completed_at"):
                    latest_attempt = attempt
                    break

            if not latest_attempt:
                # Créer une nouvelle tentative si aucune n'est en cours
                latest_attempt = await ExamService.start_exam_attempt(user_id, submission.exam_id)

            # Mettre à jour la tentative
            update_data = {
                "score": total_score,
                "max_score": max_score,
                "percentage": percentage,
                "passed": passed,
                "answers": answers_detail,
                "time_spent": submission.time_spent,
                "completed_at": datetime.now(timezone.utc)
            }
            
            # Ajouter les scores détaillés pour les examens de mathématiques
            if exam_type == "mathematics":
                update_data["qcm_score"] = qcm_score
                update_data["qcm_max_score"] = qcm_max_score
                update_data["practical_score"] = practical_score
                update_data["practical_max_score"] = practical_max_score
                if practical_answers:
                    update_data["practical_answers"] = practical_answers

            updated_attempt = await ExamAttemptRepository.update(latest_attempt["id"], update_data)

            # Si l'examen est réussi, valider le module
            module_validated = False
            if passed:
                from app.services.validation_service import ValidationService
                module_validated = await ValidationService.validate_module(
                    user_id=user_id,
                    module_id=module_id,
                    exam_attempt_id=latest_attempt["id"],
                    score=percentage
                )

            return {
                "attempt_id": updated_attempt["id"],
                "score": total_score,
                "max_score": max_score,
                "percentage": percentage,
                "passed": passed,
                "module_id": module_id,
                "module_validated": module_validated
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la soumission de l'examen: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de la soumission de l'examen: {str(e)}"
            )

    @staticmethod
    async def get_user_exam_attempts(
        user_id: str, 
        module_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Récupère les tentatives d'examen d'un utilisateur (optimisé avec limite)
        """
        try:
            if not user_id:
                return []
            
            # Limiter à 50 par défaut pour la performance
            actual_limit = min(limit, 50)
            
            if module_id:
                attempts = await ExamAttemptRepository.find_by_user_and_module(user_id, module_id)
                # Limiter les résultats même si la méthode ne le fait pas
                return attempts[:actual_limit] if attempts else []
            
            attempts = await ExamAttemptRepository.find_by_user(user_id, limit=actual_limit)
            return attempts or []
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des tentatives: {e}", exc_info=True)
            # Retourner une liste vide en cas d'erreur plutôt qu'une exception
            return []
