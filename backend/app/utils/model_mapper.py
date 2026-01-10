"""
Utilitaires pour mapper les modèles GPT-5 fictifs vers les vrais modèles OpenAI
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Mapping des modèles GPT-5 fictifs vers les vrais modèles OpenAI
MODEL_MAPPING: Dict[str, str] = {
    "gpt-5-mini": "gpt-4o-mini",   # Équivalent pédagogique (rapide et économique)
    "gpt-5.2": "gpt-4o",            # Équivalent expert (raisonnement complexe)
    "gpt-5-nano": "gpt-3.5-turbo",  # Équivalent rapide/économique (QCM, flash-cards)
}

# Coûts réels des modèles OpenAI (par 1M tokens pour l'entrée)
REAL_MODEL_COSTS: Dict[str, float] = {
    "gpt-4o-mini": 0.15,      # $0.15 / 1M tokens (input)
    "gpt-4o": 2.50,            # $2.50 / 1M tokens (input)
    "gpt-3.5-turbo": 0.50,    # $0.50 / 1M tokens (input)
    # Modèles fictifs (pour compatibilité avec le code existant)
    "gpt-5-mini": 0.15,
    "gpt-5.2": 2.50,
    "gpt-5-nano": 0.50,
}


def map_to_real_model(model: str) -> str:
    """
    Mappe un modèle GPT-5 fictif vers le vrai modèle OpenAI correspondant.
    
    Args:
        model: Nom du modèle (peut être fictif ou réel)
        
    Returns:
        Nom du vrai modèle OpenAI
        
    Examples:
        >>> map_to_real_model("gpt-5-mini")
        'gpt-4o-mini'
        >>> map_to_real_model("gpt-4o-mini")
        'gpt-4o-mini'
    """
    # Si c'est déjà un modèle réel, le retourner tel quel
    if model in ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "gpt-4", "gpt-3.5-turbo-16k"]:
        return model
    
    # Mapper les modèles fictifs vers les vrais modèles
    real_model = MODEL_MAPPING.get(model, "gpt-4o-mini")  # Fallback par défaut
    
    if model != real_model:
        logger.debug(f"Modèle '{model}' mappé vers '{real_model}'")
    
    return real_model


def get_model_cost(model: str) -> float:
    """
    Retourne le coût estimé (par 1M tokens) pour un modèle.
    
    Args:
        model: Nom du modèle (peut être fictif ou réel)
        
    Returns:
        Coût en dollars par 1M tokens (entrée)
    """
    real_model = map_to_real_model(model)
    return REAL_MODEL_COSTS.get(real_model, 2.50)  # Fallback: $2.50/M tokens (GPT-4o)


def is_real_model(model: str) -> bool:
    """
    Vérifie si un modèle est un vrai modèle OpenAI (non fictif).
    
    Args:
        model: Nom du modèle à vérifier
        
    Returns:
        True si c'est un vrai modèle, False sinon
    """
    return model in ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "gpt-4", "gpt-3.5-turbo-16k", "gpt-4-turbo"]
