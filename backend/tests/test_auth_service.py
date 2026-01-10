import pytest
from fastapi import HTTPException
from app.services.auth_service import AuthService
from app.models import UserCreate


@pytest.mark.asyncio
async def test_register_user_invalid_password():
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="weak",
        first_name="Test",
        last_name="User",
        date_of_birth="2000-01-01",
        country="FR",
    )
    with pytest.raises(HTTPException):
        await AuthService.register_user(user_data)


@pytest.mark.asyncio
async def test_register_user_success(monkeypatch):
    user_data = UserCreate(
        email="ok@example.com",
        username="okuser",
        password="StrongP@ssw0rd",
        first_name="Ok",
        last_name="User",
        date_of_birth="1995-05-10",
        country="FR",
    )

    async def fake_exists(email=None, username=None):
        return False

    async def fake_create(user_dict):
        return {**user_dict, "id": "abcd1234"}

    monkeypatch.setattr("app.repositories.user_repository.UserRepository.exists", fake_exists)
    monkeypatch.setattr("app.repositories.user_repository.UserRepository.create", fake_create)

    user = await AuthService.register_user(user_data)
    assert user["email"] == "ok@example.com"
    assert user["username"] == "okuser"
    assert "id" in user
