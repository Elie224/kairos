"""
Schémas MongoDB
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId

def serialize_doc(doc: dict, exclude_fields: Optional[List[str]] = None) -> dict:
    """Convertit un document MongoDB en dictionnaire Python"""
    if doc is None:
        return None
    
    # Créer une copie pour ne pas modifier l'original
    result = doc.copy()
    
    if "_id" in result:
        result["id"] = str(result["_id"])
        del result["_id"]
    
    # Exclure les champs sensibles par défaut
    if exclude_fields is None:
        exclude_fields = ["hashed_password", "password"]
    
    for field in exclude_fields:
        if field in result:
            del result[field]
    
    # Convertit les ObjectId en string et les datetime en ISO format
    def convert_value(value):
        if isinstance(value, ObjectId):
            return str(value)
        elif isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, dict):
            return serialize_doc(value, exclude_fields=[])
        elif isinstance(value, list):
            return [convert_value(item) for item in value]
        elif hasattr(value, '__dict__'):
            # Pour les objets personnalisés, essayer de les convertir en dict
            try:
                return serialize_doc(value.__dict__, exclude_fields=[])
            except:
                return str(value)
        return value
    
    for key, value in result.items():
        try:
            result[key] = convert_value(value)
        except Exception:
            # Si la conversion échoue, convertir en string
            try:
                result[key] = str(value)
            except Exception:
                # Si même la conversion en string échoue, supprimer la clé
                del result[key]
    
    return result

