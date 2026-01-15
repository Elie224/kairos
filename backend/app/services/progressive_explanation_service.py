"""
Service pour les explications progressives (courtes puis approfondies)
"""
from typing import Dict, Any, Optional
from app.services.ai_service import AIService
from app.services.pedagogical_memory_service import PedagogicalMemoryService
import logging

logger = logging.getLogger(__name__)


class ProgressiveExplanationService:
    """Service pour générer des explications progressives"""
    
    @staticmethod
    async def generate_short_explanation(
        question: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """Génère une explication courte initiale"""
        try:
            # Adapter selon la mémoire pédagogique
            adaptation = {}
            if user_id and subject:
                adaptation = await PedagogicalMemoryService.adapt_explanation(user_id, subject)
            
            # Construire le prompt pour réponse courte
            prompt = f"""Tu es un tuteur pédagogique. Réponds à cette question de manière CONCISE et CLAIRE.

Question: {question}

Instructions:
- Réponse courte (2-3 phrases maximum)
- Directe et précise
- Utilise des exemples simples si nécessaire
- Niveau: {adaptation.get('level', 'beginner')}
"""
            
            # Utiliser le modèle rapide pour les réponses courtes
            # Intégrer le contexte dans le message si fourni
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                prompt = f"{prompt}\n\nContexte:\n{context_str}"
            
            response = await AIService.chat_with_ai(
                user_id=user_id or "system_progressive",
                message=prompt,
                module_id=None,  # Pas de module_id spécifique pour les explications progressives
                language="fr",
                expert_mode=False  # Modèle rapide pour réponses courtes
            )
            
            return {
                "short_explanation": response.get("response", ""),
                "has_more": True,  # Toujours proposer d'approfondir
                "explanation_id": response.get("id", ""),
                "tokens_used": response.get("tokens_used", 0)
            }
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'explication courte: {e}")
            return {
                "short_explanation": "Désolé, je ne peux pas répondre pour le moment.",
                "has_more": False,
                "explanation_id": "",
                "tokens_used": 0
            }
    
    @staticmethod
    async def generate_detailed_explanation(
        question: str,
        short_explanation: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """Génère une explication détaillée approfondie"""
        try:
            # Adapter selon la mémoire pédagogique
            adaptation = {}
            if user_id and subject:
                adaptation = await PedagogicalMemoryService.adapt_explanation(user_id, subject)
            
            detail_level = adaptation.get("detail_level", "medium")
            preferred_format = adaptation.get("preferred_format", "balanced")
            examples_preferred = adaptation.get("examples_preferred", True)
            visual_aids_preferred = adaptation.get("visual_aids_preferred", True)
            
            # Construire le prompt pour réponse détaillée
            format_instructions = ""
            if preferred_format == "step_by_step":
                format_instructions = "- Explique étape par étape de manière détaillée"
            elif preferred_format == "visual":
                format_instructions = "- Utilise des analogies visuelles et des exemples concrets"
            elif preferred_format == "summary":
                format_instructions = "- Fournis un résumé structuré avec points clés"
            else:
                format_instructions = "- Fournis une explication équilibrée avec détails et exemples"
            
            prompt = f"""Tu es un tuteur pédagogique expert. Fournis une explication DÉTAILLÉE et APPROFONDIE.

Question: {question}
Réponse courte déjà donnée: {short_explanation}

Instructions:
{format_instructions}
- Niveau de détail: {detail_level}
- {'Inclus des exemples concrets' if examples_preferred else 'Concentre-toi sur les concepts'}
- {'Utilise des analogies et visualisations' if visual_aids_preferred else 'Approche théorique'}
- Explique le "pourquoi" et le "comment"
- Structure claire avec sections si nécessaire
"""
            
            # Utiliser le modèle expert pour les réponses détaillées
            # Intégrer le contexte dans le message si fourni
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                prompt = f"{prompt}\n\nContexte:\n{context_str}"
            
            response = await AIService.chat_with_ai(
                user_id=user_id or "system_progressive",
                message=prompt,
                module_id=None,  # Pas de module_id spécifique pour les explications progressives
                language="fr",
                expert_mode=True  # Modèle expert pour réponses détaillées
            )
            
            return {
                "detailed_explanation": response.get("response", ""),
                "explanation_id": response.get("id", ""),
                "tokens_used": response.get("tokens_used", 0)
            }
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'explication détaillée: {e}")
            return {
                "detailed_explanation": "Désolé, je ne peux pas fournir plus de détails pour le moment.",
                "explanation_id": "",
                "tokens_used": 0
            }
