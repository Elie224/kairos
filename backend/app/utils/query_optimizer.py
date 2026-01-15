"""
Optimiseur de requêtes MongoDB pour performance maximale
"""
from typing import Dict, Any, Optional, List
from pymongo import ReadPreference
import logging

logger = logging.getLogger(__name__)


def optimize_query(
    query: Dict[str, Any],
    hint: Optional[List[tuple]] = None,
    read_preference: ReadPreference = ReadPreference.PRIMARY_PREFERRED
) -> Dict[str, Any]:
    """
    Optimise une requête MongoDB
    
    Args:
        query: Requête MongoDB
        hint: Index hint pour forcer l'utilisation d'un index spécifique
        read_preference: Préférence de lecture (PRIMARY_PREFERRED pour performance)
    
    Returns:
        Requête optimisée avec hints
    """
    optimized = {
        "query": query,
        "hint": hint,
        "read_preference": read_preference
    }
    return optimized


def add_read_preference(cursor, read_preference: ReadPreference = ReadPreference.PRIMARY_PREFERRED):
    """
    Ajoute une préférence de lecture à un cursor MongoDB
    
    Args:
        cursor: Cursor MongoDB
        read_preference: Préférence de lecture
    
    Returns:
        Cursor avec préférence de lecture
    """
    # Motor/MongoDB async supporte read_preference via with_options
    try:
        return cursor.with_options(read_preference=read_preference)
    except Exception:
        # Si read_preference n'est pas supporté, retourner le cursor tel quel
        return cursor


def optimize_aggregation_pipeline(
    pipeline: List[Dict[str, Any]],
    allow_disk_use: bool = True,
    batch_size: int = 1000
) -> Dict[str, Any]:
    """
    Optimise un pipeline d'agrégation MongoDB
    
    Args:
        pipeline: Pipeline d'agrégation
        allow_disk_use: Autoriser l'utilisation du disque pour grandes collections
        batch_size: Taille du batch pour les résultats
    
    Returns:
        Options d'agrégation optimisées
    """
    return {
        "pipeline": pipeline,
        "allowDiskUse": allow_disk_use,
        "batchSize": batch_size
    }
