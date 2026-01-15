"""
Tests pour la mémoire pédagogique
"""
import pytest
from app.services.pedagogical_memory_service import PedagogicalMemoryService
from app.repositories.pedagogical_memory_repository import PedagogicalMemoryRepository


@pytest.mark.asyncio
async def test_get_memory_nonexistent_user():
    """Test récupération mémoire pour utilisateur inexistant"""
    memory = await PedagogicalMemoryService.get_memory("nonexistent_user")
    assert memory is None


@pytest.mark.asyncio
async def test_get_subject_level_default():
    """Test récupération niveau par défaut"""
    level = await PedagogicalMemoryService.get_subject_level("test_user", "mathematics")
    assert level == "beginner"


@pytest.mark.asyncio
async def test_record_error():
    """Test enregistrement d'erreur"""
    user_id = "test_user_123"
    await PedagogicalMemoryService.record_error(user_id, "dérivées", "calcul")
    
    errors = await PedagogicalMemoryService.get_frequent_errors(user_id, 5)
    assert len(errors) > 0
    assert errors[0]["concept"] == "dérivées"


@pytest.mark.asyncio
async def test_update_level():
    """Test mise à jour niveau"""
    user_id = "test_user_456"
    await PedagogicalMemoryService.update_level(user_id, "mathematics", "intermediate", 0.75)
    
    level = await PedagogicalMemoryService.get_subject_level(user_id, "mathematics")
    assert level == "intermediate"
