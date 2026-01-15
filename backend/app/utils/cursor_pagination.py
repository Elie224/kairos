"""
Pagination basée sur les cursors pour meilleures performances
Remplace skip/limit pour éviter les problèmes de performance avec de grandes collections
"""
from typing import Optional, Dict, Any, List
from bson import ObjectId
import base64
import json
from datetime import datetime


def encode_cursor(cursor_data: Dict[str, Any]) -> str:
    """
    Encode un cursor pour la pagination
    
    Args:
        cursor_data: Données du cursor (ex: {"_id": ObjectId(...), "created_at": datetime})
    
    Returns:
        String encodée en base64
    """
    # Convertir ObjectId et datetime en strings pour sérialisation
    serializable = {}
    for key, value in cursor_data.items():
        if isinstance(value, ObjectId):
            serializable[key] = str(value)
        elif isinstance(value, datetime):
            serializable[key] = value.isoformat()
        else:
            serializable[key] = value
    
    json_str = json.dumps(serializable, default=str)
    return base64.urlsafe_b64encode(json_str.encode()).decode()


def decode_cursor(cursor_str: str) -> Dict[str, Any]:
    """
    Décode un cursor pour la pagination
    
    Args:
        cursor_str: String encodée en base64
    
    Returns:
        Dictionnaire avec les données du cursor
    """
    try:
        json_str = base64.urlsafe_b64decode(cursor_str.encode()).decode()
        data = json.loads(json_str)
        
        # Reconvertir les strings en ObjectId et datetime si nécessaire
        if "_id" in data:
            try:
                data["_id"] = ObjectId(data["_id"])
            except Exception:
                pass
        
        if "created_at" in data:
            try:
                data["created_at"] = datetime.fromisoformat(data["created_at"])
            except Exception:
                pass
        
        return data
    except Exception:
        return {}


def build_cursor_query(
    cursor: Optional[str] = None,
    sort_field: str = "created_at",
    sort_direction: int = -1
) -> Dict[str, Any]:
    """
    Construit une requête MongoDB basée sur un cursor
    
    Args:
        cursor: Cursor encodé (optionnel)
        sort_field: Champ de tri (par défaut: created_at)
        sort_direction: Direction du tri (-1 pour décroissant, 1 pour croissant)
    
    Returns:
        Dictionnaire de requête MongoDB
    """
    if not cursor:
        return {}
    
    cursor_data = decode_cursor(cursor)
    if not cursor_data:
        return {}
    
    # Construire la requête pour récupérer les documents après le cursor
    if sort_direction == -1:  # Décroissant
        query = {
            "$or": [
                {sort_field: {"$lt": cursor_data.get(sort_field)}},
                {
                    "$and": [
                        {sort_field: cursor_data.get(sort_field)},
                        {"_id": {"$lt": cursor_data.get("_id")}}
                    ]
                }
            ]
        }
    else:  # Croissant
        query = {
            "$or": [
                {sort_field: {"$gt": cursor_data.get(sort_field)}},
                {
                    "$and": [
                        {sort_field: cursor_data.get(sort_field)},
                        {"_id": {"$gt": cursor_data.get("_id")}}
                    ]
                }
            ]
        }
    
    return query


def create_cursor_from_doc(doc: Dict[str, Any], sort_field: str = "created_at") -> str:
    """
    Crée un cursor à partir d'un document
    
    Args:
        doc: Document MongoDB
        sort_field: Champ de tri utilisé
    
    Returns:
        Cursor encodé
    """
    cursor_data = {
        "_id": doc.get("_id"),
        sort_field: doc.get(sort_field)
    }
    return encode_cursor(cursor_data)


def paginate_with_cursor(
    cursor_obj,
    limit: int,
    sort_field: str = "created_at",
    sort_direction: int = -1,
    cursor: Optional[str] = None
) -> tuple[List[Dict[str, Any]], Optional[str], Optional[str]]:
    """
    Pagine des résultats avec un cursor
    
    Args:
        cursor_obj: Cursor MongoDB
        limit: Nombre de résultats à retourner
        sort_field: Champ de tri
        sort_direction: Direction du tri
        cursor: Cursor de départ (optionnel)
    
    Returns:
        Tuple (results, next_cursor, prev_cursor)
    """
    # Construire la requête avec le cursor
    query = build_cursor_query(cursor, sort_field, sort_direction)
    
    # Appliquer la requête si elle existe
    if query:
        cursor_obj = cursor_obj.find(query)
    
    # Trier et limiter
    cursor_obj = cursor_obj.sort(sort_field, sort_direction).limit(limit + 1)  # +1 pour détecter s'il y a plus
    
    # Récupérer les résultats
    results = []
    async def fetch_results():
        count = 0
        async for doc in cursor_obj:
            if count < limit:
                results.append(doc)
                count += 1
            else:
                # Il y a plus de résultats, créer le next_cursor
                return create_cursor_from_doc(doc, sort_field)
        return None
    
    # Note: Cette fonction doit être appelée avec await dans un contexte async
    # Pour l'instant, on retourne une fonction async
    return results, None, None
