"""
Fallback gracieux pour l'IA - Réponses simplifiées si OpenAI indisponible
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AIFallback:
    """Gestion du fallback gracieux pour l'IA"""
    
    @staticmethod
    def get_fallback_response(message: str, language: str = "fr") -> Dict[str, Any]:
        """
        Retourne une réponse de fallback si OpenAI est indisponible
        
        Returns:
            {
                "response": str,
                "suggestions": List[str],
                "fallback": True
            }
        """
        if language == "en":
            return {
                "response": """I apologize, but the AI service is temporarily unavailable.

Here's a simplified explanation based on your question:

**Quick Answer:**
I'm currently unable to provide a detailed AI-powered response. Please try again in a few moments.

**What you can do:**
- Check our course modules for detailed explanations
- Review previous lessons on this topic
- Try asking your question again in a moment

**Alternative:**
If you need immediate help, please contact our support team or check the FAQ section.""",
                "suggestions": [
                    "Try again in a moment",
                    "Check course modules",
                    "Contact support"
                ],
                "fallback": True
            }
        else:
            return {
                "response": """Je m'excuse, mais le service IA est temporairement indisponible.

Voici une explication simplifiée basée sur votre question :

**Réponse rapide :**
Je ne peux actuellement pas fournir une réponse détaillée assistée par IA. Veuillez réessayer dans quelques instants.

**Ce que vous pouvez faire :**
- Consulter nos modules de cours pour des explications détaillées
- Réviser les leçons précédentes sur ce sujet
- Réessayer votre question dans un moment

**Alternative :**
Si vous avez besoin d'aide immédiate, veuillez contacter notre équipe de support ou consulter la section FAQ.""",
                "suggestions": [
                    "Réessayer dans un moment",
                    "Consulter les modules",
                    "Contacter le support"
                ],
                "fallback": True
            }
    
    @staticmethod
    def get_timeout_response(message: str, language: str = "fr") -> Dict[str, Any]:
        """Réponse en cas de timeout"""
        if language == "en":
            return {
                "response": """The AI service is taking longer than expected to respond.

**What happened:**
Your question requires a complex analysis that is taking more time than usual.

**Options:**
1. Wait a moment and try again
2. Try rephrasing your question more simply
3. Use GPT-5-mini mode for faster responses

We apologize for the inconvenience.""",
                "suggestions": [
                    "Try again",
                    "Simplify question",
                    "Use fast mode"
                ],
                "fallback": True,
                "timeout": True
            }
        else:
            return {
                "response": """Le service IA prend plus de temps que prévu pour répondre.

**Ce qui s'est passé :**
Votre question nécessite une analyse complexe qui prend plus de temps que d'habitude.

**Options :**
1. Attendez un moment et réessayez
2. Essayez de reformuler votre question plus simplement
3. Utilisez le mode GPT-5-mini pour des réponses plus rapides

Nous nous excusons pour ce désagrément.""",
                "suggestions": [
                    "Réessayer",
                    "Simplifier la question",
                    "Mode rapide"
                ],
                "fallback": True,
                "timeout": True
            }
    
    @staticmethod
    def get_rate_limit_response(language: str = "fr") -> Dict[str, Any]:
        """Réponse en cas de rate limit"""
        if language == "en":
            return {
                "response": """The AI service is currently experiencing high demand.

**What happened:**
Too many requests are being processed at the same time.

**What to do:**
- Please wait a few minutes before trying again
- Consider using GPT-5-mini for faster processing
- Check back later during off-peak hours

Thank you for your patience.""",
                "suggestions": [
                    "Wait and retry",
                    "Use fast mode",
                    "Try later"
                ],
                "fallback": True,
                "rate_limit": True
            }
        else:
            return {
                "response": """Le service IA connaît actuellement une forte demande.

**Ce qui s'est passé :**
Trop de requêtes sont traitées en même temps.

**Que faire :**
- Veuillez attendre quelques minutes avant de réessayer
- Envisagez d'utiliser GPT-5-mini pour un traitement plus rapide
- Réessayez plus tard pendant les heures creuses

Merci de votre patience.""",
                "suggestions": [
                    "Attendre et réessayer",
                    "Mode rapide",
                    "Réessayer plus tard"
                ],
                "fallback": True,
                "rate_limit": True
            }











