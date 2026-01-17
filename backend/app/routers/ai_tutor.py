"""
Routeur pour le tutorat IA - Refactorisé avec services
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
from app.models import AIChatRequest, AIChatResponse, QuizGenerateRequest, QuizResponse, ImmersiveContextRequest, ImmersiveContextResponse
# Authentification supprimée - toutes les routes sont publiques
from app.services.ai_service import AIService
from app.services.ai_routing_service import AIRoutingService
import json
import logging
import asyncio
import inspect
import base64
import io

logger = logging.getLogger(__name__)


def safe_str(obj):
    """Convertit un objet en string de manière sécurisée, évitant les coroutines"""
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if inspect.iscoroutine(obj):
        return "Une coroutine a été détectée (erreur de programmation)"
    if inspect.iscoroutinefunction(obj):
        return "Une fonction coroutine a été détectée (erreur de programmation)"
    try:
        return str(obj)
    except Exception:
        return "Erreur lors de la conversion en string"

router = APIRouter()


@router.post("/chat", response_model=AIChatResponse)
async def chat_with_ai(request: AIChatRequest):
    """Chat avec Kaïrox (mode standard, Expert ou Research) avec cache intelligent et historique (route publique)"""
    language = request.language or "fr"
    user_id = "anonymous"  # Auth supprimée
    
    # Récupérer l'historique de conversation de l'utilisateur si non fourni par le frontend
    conversation_history = request.conversation_history
    if not conversation_history and user_id and request.module_id:
        try:
            from app.services.user_history_service import UserHistoryService
            # Récupérer les 10 derniers échanges pour ce module
            history_entries = await UserHistoryService.get_user_history(
                user_id=user_id,
                module_id=request.module_id,
                limit=10
            )
            # Convertir en format messages OpenAI
            conversation_history = []
            for entry in history_entries:
                conversation_history.append({
                    "role": "user",
                    "content": entry.get("question", "")
                })
                conversation_history.append({
                    "role": "assistant",
                    "content": entry.get("answer", "")
                })
        except Exception as e:
            logger.debug(f"Erreur récupération historique: {safe_str(e)}")
            conversation_history = None
    
    result = await AIService.chat_with_ai(
        message=request.message,
        user_id=user_id,
        module_id=request.module_id,
        language=language,
        expert_mode=request.expert_mode or False,
        research_mode=request.research_mode or False,
        conversation_history=conversation_history
    )
    
    # Sauvegarder l'historique de conversation après chaque échange
    if user_id and result and result.get("response"):
        try:
            from app.services.user_history_service import UserHistoryService
            from app.repositories.module_repository import ModuleRepository
            from app.models.user_history import Subject
            
            # Déterminer le sujet à partir du module
            subject = None
            if request.module_id:
                module = await ModuleRepository.find_by_id(request.module_id)
                if module:
                    module_subject = module.get("subject", "").lower()
                    if module_subject == "computer_science":
                        subject = Subject.COMPUTER_SCIENCE
                    elif module_subject == "mathematics":
                        subject = Subject.MATHEMATICS
            
            # Sauvegarder dans l'historique
            await UserHistoryService.store_answer(
                user_id=user_id,
                question=request.message,
                answer=result.get("response", ""),
                model_used=result.get("model_used", "gpt-5-mini"),
                subject=subject,
                module_id=request.module_id,
                language=language
            )
            logger.info(f"Historique sauvegardé pour utilisateur {user_id}, module {request.module_id}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'historique: {safe_str(e)}", exc_info=True)
            # Ne pas faire échouer la requête si la sauvegarde échoue
    
    # Vérifier qu'aucune coroutine n'est présente dans le résultat avant de le retourner
    if isinstance(result, dict):
        cleaned_result = {}
        for key, value in result.items():
            if inspect.iscoroutine(value):
                logger.error(f"Coroutine détectée dans result['{key}'] - remplacement par message d'erreur")
                cleaned_result[key] = "Erreur: valeur coroutine détectée"
            elif inspect.iscoroutinefunction(value):
                logger.error(f"Fonction coroutine détectée dans result['{key}'] - remplacement par message d'erreur")
                cleaned_result[key] = "Erreur: fonction coroutine détectée"
            else:
                cleaned_result[key] = value
        return cleaned_result
    
    return result


@router.post("/chat/stream")
async def chat_with_ai_stream(request: AIChatRequest):
    """Chat avec Kaïrox en streaming (optimisé pour 100k utilisateurs) avec historique de conversation (route publique)"""
    language = request.language or "fr"
    user_id = "anonymous"  # Auth supprimée
    
    # Récupérer le contexte du module si disponible
    context = None
    if request.module_id:
        from app.repositories.module_repository import ModuleRepository
        module = await ModuleRepository.find_by_id(request.module_id)
        if module:
            context = f"{module.get('title', '')} - {module.get('description', '')}"
    
    # Récupérer l'historique de conversation de l'utilisateur
    conversation_history = None
    if user_id and request.module_id:
        try:
            from app.services.user_history_service import UserHistoryService
            from app.models.user_history import Subject
            # Récupérer les 10 derniers échanges pour ce module
            history_entries = await UserHistoryService.get_user_history(
                user_id=user_id,
                module_id=request.module_id,
                limit=10
            )
            # Convertir en format messages OpenAI
            conversation_history = []
            for entry in history_entries:
                conversation_history.append({
                    "role": "user",
                    "content": entry.get("question", "")
                })
                conversation_history.append({
                    "role": "assistant",
                    "content": entry.get("answer", "")
                })
        except Exception as e:
            logger.debug(f"Erreur récupération historique: {safe_str(e)}")
            conversation_history = None
    
    # Utiliser l'historique envoyé par le frontend s'il est disponible
    if request.conversation_history:
        conversation_history = request.conversation_history
    
    # Forcer le modèle selon le mode (priorité: research > expert)
    if request.research_mode:
        force_model = "gpt-5.2"  # Utiliser GPT-5.2 pour research mode
    elif request.expert_mode:
        force_model = "gpt-5.2"
    else:
        force_model = None
    
    async def generate():
        full_response = ""  # Accumuler la réponse complète pour sauvegarder l'historique
        try:
            async for chunk in AIRoutingService.chat_stream(
                message=request.message,
                module_id=request.module_id,
                context=context,
                language=language,
                force_model=force_model,
                conversation_history=conversation_history
            ):
                # S'assurer que chunk est une string avant de le sérialiser (éviter les coroutines)
                chunk_str = safe_str(chunk) if chunk else ""
                if chunk_str and not chunk_str.startswith("Erreur:"):
                    full_response += chunk_str  # Accumuler la réponse
                try:
                    yield f"data: {json.dumps({'content': chunk_str})}\n\n"
                except Exception as json_error:
                    logger.error(f"Erreur sérialisation chunk: {safe_str(json_error)}")
                    # Essayer avec un message simplifié
                    yield f"data: {json.dumps({'content': chunk_str[:1000] if len(chunk_str) > 1000 else chunk_str})}\n\n"
            yield "data: [DONE]\n\n"
            
            # Sauvegarder l'historique après la fin du streaming
            if user_id and full_response and not full_response.startswith("Erreur:"):
                try:
                    from app.services.user_history_service import UserHistoryService
                    from app.repositories.module_repository import ModuleRepository
                    from app.models.user_history import Subject
                    
                    # Déterminer le sujet à partir du module
                    subject = None
                    if request.module_id:
                        module = await ModuleRepository.find_by_id(request.module_id)
                        if module:
                            module_subject = module.get("subject", "").lower()
                            if module_subject == "computer_science":
                                subject = Subject.COMPUTER_SCIENCE
                            elif module_subject == "mathematics":
                                subject = Subject.MATHEMATICS
                    
                    # Déterminer le modèle utilisé
                    model_used = force_model or "gpt-5-mini"
                    if request.research_mode or request.expert_mode:
                        model_used = "gpt-5.2"
                    
                    # Sauvegarder dans l'historique
                    await UserHistoryService.store_answer(
                        user_id=user_id,
                        question=request.message,
                        answer=full_response,
                        model_used=model_used,
                        subject=subject,
                        module_id=request.module_id,
                        language=language
                    )
                    logger.info(f"Historique sauvegardé pour utilisateur {user_id}, module {request.module_id}")
                except Exception as e:
                    logger.error(f"Erreur lors de la sauvegarde de l'historique: {safe_str(e)}", exc_info=True)
                    # Ne pas faire échouer la requête si la sauvegarde échoue
        except Exception as e:
            logger.error(f"Erreur dans generate(): {safe_str(e)}", exc_info=True)
            # S'assurer que l'erreur est bien convertie en string de manière sécurisée
            error_message = safe_str(e) if e else "Une erreur inconnue s'est produite"
            try:
                yield f"data: {json.dumps({'content': f'Erreur: {error_message}'})}\n\n"
            except Exception as json_error:
                # Si même la sérialisation JSON échoue, envoyer un message simple
                logger.error(f"Erreur sérialisation JSON: {safe_str(json_error)}")
                yield f"data: {json.dumps({'content': 'Erreur lors du traitement de la requête'})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Désactiver le buffering nginx
        }
    )


@router.post("/chat/stream/with-files")
async def chat_with_ai_stream_files(
    message: str = Form(...),
    module_id: Optional[str] = Form(None),
    language: str = Form("fr"),
    expert_mode: bool = Form(False),
    research_mode: bool = Form(False),
    conversation_history: Optional[str] = Form(None),  # JSON string
    files: List[UploadFile] = File([])
):
    """
    Chat avec Kaïrox en streaming avec support des fichiers/images.
    Utilise OpenAI Vision pour analyser les images. (route publique)
    """
    user_id = "anonymous"  # Auth supprimée
    
    # Parser l'historique de conversation si fourni
    parsed_history = None
    if conversation_history:
        try:
            parsed_history = json.loads(conversation_history)
        except Exception as e:
            logger.debug(f"Erreur parsing conversation_history: {safe_str(e)}")
    
    # Récupérer le contexte du module si disponible
    context = None
    if module_id:
        from app.repositories.module_repository import ModuleRepository
        module = await ModuleRepository.find_by_id(module_id)
        if module:
            context = f"{module.get('title', '')} - {module.get('description', '')}"
    
    # Récupérer l'historique de conversation de l'utilisateur si non fourni
    if not parsed_history and user_id and module_id:
        try:
            from app.services.user_history_service import UserHistoryService
            history_entries = await UserHistoryService.get_user_history(
                user_id=user_id,
                module_id=module_id,
                limit=10
            )
            parsed_history = []
            for entry in history_entries:
                parsed_history.append({
                    "role": "user",
                    "content": entry.get("question", "")
                })
                parsed_history.append({
                    "role": "assistant",
                    "content": entry.get("answer", "")
                })
        except Exception as e:
            logger.debug(f"Erreur récupération historique: {safe_str(e)}")
            parsed_history = None
    
    # Traiter les fichiers/images/PDFs
    image_contents = []
    for file in files:
        try:
            # Lire le contenu du fichier
            contents = await file.read()
            
            # Vérifier le type MIME
            content_type = file.content_type or ""
            filename = file.filename or ""
            
            # Vérifier si c'est une image
            if content_type.startswith("image/"):
                # Encoder en base64
                base64_image = base64.b64encode(contents).decode('utf-8')
                image_contents.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{content_type};base64,{base64_image}"
                    }
                })
            elif content_type == "application/pdf" or filename.lower().endswith(".pdf"):
                # Convertir le PDF en images (pages)
                try:
                    import fitz  # PyMuPDF
                    pdf_doc = fitz.open(stream=contents, filetype="pdf")
                    # Convertir chaque page en image (maximum 10 pages pour éviter les limites)
                    max_pages = min(10, len(pdf_doc))
                    for page_num in range(max_pages):
                        page = pdf_doc[page_num]
                        # Rendre la page en image avec une résolution raisonnable
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom pour meilleure qualité
                        img_bytes = pix.tobytes("png")
                        base64_image = base64.b64encode(img_bytes).decode('utf-8')
                        image_contents.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        })
                    pdf_doc.close()
                    logger.info(f"PDF '{filename}' converti en {max_pages} image(s)")
                except ImportError:
                    logger.warning("PyMuPDF (fitz) non installé. Installez-le avec: pip install PyMuPDF")
                    logger.warning(f"Impossible de traiter le PDF '{filename}' - conversion en image non disponible")
                except Exception as pdf_error:
                    logger.error(f"Erreur lors de la conversion du PDF '{filename}': {safe_str(pdf_error)}")
            elif (content_type in ["application/msword", 
                                   "application/vnd.openxmlformats-officedocument.wordprocessingml.document"] or
                  filename.lower().endswith((".doc", ".docx"))):
                # Pour Word, on pourrait extraire le texte ou convertir en images
                # Pour l'instant, on logue un avertissement
                logger.warning(f"Fichier Word '{filename}' détecté mais non traité automatiquement. "
                             f"Veuillez convertir en PDF ou image pour l'analyse.")
            elif (content_type in ["application/vnd.ms-powerpoint",
                                   "application/vnd.openxmlformats-officedocument.presentationml.presentation"] or
                  filename.lower().endswith((".ppt", ".pptx"))):
                # Pour PowerPoint, on pourrait extraire le texte ou convertir en images
                logger.warning(f"Fichier PowerPoint '{filename}' détecté mais non traité automatiquement. "
                             f"Veuillez convertir en PDF ou image pour l'analyse.")
            else:
                logger.warning(f"Type de fichier non supporté: {content_type} (fichier: {filename})")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du fichier {file.filename}: {safe_str(e)}")
    
    # Forcer le modèle selon le mode (priorité: research > expert)
    if research_mode:
        force_model = "gpt-5.2"  # Utiliser GPT-5.2 pour research mode
    elif expert_mode:
        force_model = "gpt-5.2"
    else:
        # Utiliser GPT-5.2 avec vision si des images sont présentes (supporte la vision)
        force_model = "gpt-5.2" if image_contents else None
    
    async def generate():
        full_response = ""  # Accumuler la réponse complète pour sauvegarder l'historique
        try:
            # Construire le message avec images si présentes
            user_message_content = []
            
            # Ajouter le texte du message
            if message:
                user_message_content.append({
                    "type": "text",
                    "text": message
                })
            
            # Ajouter les images
            user_message_content.extend(image_contents)
            
            async for chunk in AIRoutingService.chat_stream_with_vision(
                message_content=user_message_content,
                module_id=module_id,
                context=context,
                language=language,
                force_model=force_model,
                conversation_history=parsed_history
            ):
                chunk_str = safe_str(chunk) if chunk else ""
                if chunk_str and not chunk_str.startswith("Erreur:"):
                    full_response += chunk_str  # Accumuler la réponse
                try:
                    yield f"data: {json.dumps({'content': chunk_str})}\n\n"
                except Exception as json_error:
                    logger.error(f"Erreur sérialisation chunk: {safe_str(json_error)}")
                    yield f"data: {json.dumps({'content': chunk_str[:1000] if len(chunk_str) > 1000 else chunk_str})}\n\n"
            yield "data: [DONE]\n\n"
            
            # Sauvegarder l'historique après la fin du streaming
            if user_id and full_response and not full_response.startswith("Erreur:"):
                try:
                    from app.services.user_history_service import UserHistoryService
                    from app.repositories.module_repository import ModuleRepository
                    from app.models.user_history import Subject
                    
                    # Déterminer le sujet à partir du module
                    subject = None
                    if module_id:
                        module = await ModuleRepository.find_by_id(module_id)
                        if module:
                            module_subject = module.get("subject", "").lower()
                            if module_subject == "computer_science":
                                subject = Subject.COMPUTER_SCIENCE
                            elif module_subject == "mathematics":
                                subject = Subject.MATHEMATICS
                    
                    # Déterminer le modèle utilisé
                    model_used = force_model or "gpt-5.2"  # Vision utilise GPT-5.2
                    
                    # Sauvegarder dans l'historique
                    await UserHistoryService.store_answer(
                        user_id=user_id,
                        question=message,
                        answer=full_response,
                        model_used=model_used,
                        subject=subject,
                        module_id=module_id,
                        language=language,
                        metadata={"has_files": len(files) > 0, "file_count": len(files)}
                    )
                    logger.info(f"Historique sauvegardé pour utilisateur {user_id}, module {module_id} (avec fichiers)")
                except Exception as e:
                    logger.error(f"Erreur lors de la sauvegarde de l'historique: {safe_str(e)}", exc_info=True)
                    # Ne pas faire échouer la requête si la sauvegarde échoue
        except Exception as e:
            logger.error(f"Erreur dans generate(): {safe_str(e)}", exc_info=True)
            error_message = safe_str(e) if e else "Une erreur inconnue s'est produite"
            try:
                yield f"data: {json.dumps({'content': f'Erreur: {error_message}'})}\n\n"
            except Exception as json_error:
                logger.error(f"Erreur sérialisation JSON: {safe_str(json_error)}")
                yield f"data: {json.dumps({'content': 'Erreur lors du traitement de la requête'})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/immersive-context", response_model=ImmersiveContextResponse)
async def get_immersive_context(request: ImmersiveContextRequest):
    """Obtient un contexte IA pour une expérience immersive (route publique)"""
    return await AIService.get_immersive_context(
        module_id=request.module_id,
        mode=request.mode,
        scene_type=request.scene_type
    )


@router.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizGenerateRequest):
    """Génère un quiz personnalisé basé sur un module (route publique)"""
    # Validation serveur stricte du nombre de questions (max 50)
    if request.num_questions < 1 or request.num_questions > 50:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nombre de questions doit être entre 1 et 50"
        )
    
    difficulty = request.difficulty.value if request.difficulty else None
    return await AIService.generate_quiz(
        module_id=request.module_id,
        num_questions=request.num_questions,
        difficulty=difficulty
    )
