"""
Utilitaire pour nettoyer et parser le JSON généré par OpenAI
Gère les caractères de contrôle invalides et autres problèmes de formatage
"""
import json
import re
import logging

logger = logging.getLogger(__name__)


def clean_json_string(json_str: str) -> str:
    """
    Nettoie une chaîne JSON pour éliminer les caractères de contrôle invalides
    et autres problèmes de formatage courants
    """
    if not json_str:
        return json_str
    
    # Étape 1: Supprimer les caractères de contrôle invalides
    # Les caractères de contrôle valides en JSON sont: \n, \r, \t (mais seulement échappés)
    # On remplace les autres caractères de contrôle par des espaces
    json_str = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', ' ', json_str)
    
    # Étape 2: Échapper les retours à la ligne non échappés dans les chaînes JSON
    # On parcourt caractère par caractère pour identifier les chaînes
    result = []
    in_string = False
    escape_next = False
    i = 0
    
    while i < len(json_str):
        char = json_str[i]
        
        if escape_next:
            result.append(char)
            escape_next = False
        elif char == '\\':
            result.append(char)
            escape_next = True
        elif char == '"' and not escape_next:
            in_string = not in_string
            result.append(char)
        elif in_string:
            # Dans une chaîne, échapper les caractères spéciaux
            if char == '\n':
                result.append('\\n')
            elif char == '\r':
                result.append('\\r')
            elif char == '\t':
                result.append('\\t')
            elif char == '"':
                result.append('\\"')
            elif char == '\\':
                result.append('\\\\')
            else:
                result.append(char)
        else:
            result.append(char)
        
        i += 1
    
    cleaned = ''.join(result)
    
    # Dernière tentative: supprimer les caractères de contrôle restants
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)
    
    return cleaned


def fix_unterminated_strings(json_str: str) -> str:
    """
    Corrige les chaînes JSON non terminées en fermant les guillemets manquants
    """
    result = []
    in_string = False
    escape_next = False
    string_start = -1
    i = 0
    
    while i < len(json_str):
        char = json_str[i]
        
        if escape_next:
            result.append(char)
            escape_next = False
        elif char == '\\':
            result.append(char)
            escape_next = True
        elif char == '"' and not escape_next:
            if not in_string:
                # Début de chaîne
                in_string = True
                string_start = len(result)
                result.append(char)
            else:
                # Fin de chaîne
                in_string = False
                result.append(char)
        else:
            result.append(char)
        
        i += 1
    
    # Si on est encore dans une chaîne à la fin, la fermer
    if in_string:
        result.append('"')
    
    return ''.join(result)


def safe_json_loads(json_str: str, fallback=None):
    """
    Parse un JSON de manière sécurisée avec nettoyage automatique
    """
    if not json_str:
        return fallback
    
    # Essayer de parser directement
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Extraire le JSON si la chaîne contient du texte avant/après
    json_start = json_str.find('{')
    json_end = json_str.rfind('}') + 1
    
    if json_start >= 0 and json_end > json_start:
        json_content = json_str[json_start:json_end]
        
        # Essayer de parser
        try:
            return json.loads(json_content)
        except json.JSONDecodeError as e:
            # Si c'est une erreur de chaîne non terminée, essayer de la corriger
            if "Unterminated string" in str(e) or "Expecting property name" in str(e):
                try:
                    fixed = fix_unterminated_strings(json_content)
                    return json.loads(fixed)
                except json.JSONDecodeError:
                    pass
        
        # Nettoyer et réessayer
        try:
            cleaned = clean_json_string(json_content)
            # Essayer de corriger les chaînes non terminées
            fixed = fix_unterminated_strings(cleaned)
            return json.loads(fixed)
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON même après nettoyage: {e}")
            logger.error(f"Contenu problématique (premiers 1000 caractères): {json_content[:1000]}")
            # Dernière tentative : tronquer à la dernière accolade fermante valide
            try:
                # Trouver la dernière accolade fermante complète
                last_brace = json_content.rfind('}')
                if last_brace > 0:
                    truncated = json_content[:last_brace + 1]
                    # Fermer toutes les chaînes ouvertes
                    fixed = fix_unterminated_strings(truncated)
                    return json.loads(fixed)
            except:
                pass
            return fallback
    
    return fallback
