import pytest
from fastapi import HTTPException
from app.services.module_service import ModuleService
from app.models import ModuleCreate


@pytest.mark.asyncio
async def test_create_module_too_large_content():
    # Create a very large content to trigger size validation
    huge_text = "a" * 300000
    module_data = ModuleCreate(
        title="Test Module",
        description="Desc",
        subject="computer_science",
        difficulty="beginner",
        estimated_time=10,
        content={"text": huge_text},
        learning_objectives=["Obj1"]
    )
    with pytest.raises(HTTPException):
        await ModuleService.create_module(module_data)


@pytest.mark.asyncio
async def test_create_module_success(monkeypatch):
    module_data = ModuleCreate(
        title="Test Module",
        description="Desc",
        subject="computer_science",
        difficulty="beginner",
        estimated_time=10,
        content={"text": "small"},
        learning_objectives=["Obj1"]
    )

    async def fake_create(module_dict):
        return {**module_dict, "id": "mod123"}

    monkeypatch.setattr("app.repositories.module_repository.ModuleRepository.create", fake_create)
    module = await ModuleService.create_module(module_data)
    assert module["title"] == "Test Module"
    assert module["id"] == "mod123"
