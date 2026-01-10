import pytest
from fastapi import HTTPException
from datetime import timedelta

from app.services.auth_service import AuthService
from app.config import settings


@pytest.mark.asyncio
async def test_authenticate_with_google_create_user(monkeypatch):
    # Préparer un idinfo valide
    fake_idinfo = {
        'aud': 'fake-google-client.apps.googleusercontent.com',
        'sub': '1234567890',
        'email': 'newuser@example.com',
        'email_verified': True,
        'name': 'New User',
        'given_name': 'New',
        'family_name': 'User',
        'picture': 'https://example.com/avatar.png'
    }

    # Monkeypatch des vérifications Google et des repository
    monkeypatch.setattr('app.services.auth_service.id_token.verify_oauth2_token', lambda token, request, audience: fake_idinfo)

    # Forcer le client id dans settings
    monkeypatch.setattr(settings, 'google_client_id', 'fake-google-client.apps.googleusercontent.com')

    async def fake_find_by_email(email):
        return None

    async def fake_find_by_username(username):
        return None

    async def fake_create(user_dict):
        return {**user_dict, 'id': 'abcd1234'}

    monkeypatch.setattr('app.repositories.user_repository.UserRepository.find_by_email', fake_find_by_email)
    monkeypatch.setattr('app.repositories.user_repository.UserRepository.find_by_username', fake_find_by_username)
    monkeypatch.setattr('app.repositories.user_repository.UserRepository.create', fake_create)

    tokens = await AuthService.authenticate_with_google('fake-token')
    assert 'access_token' in tokens
    assert 'refresh_token' in tokens
    assert tokens['user']['email'] == 'newuser@example.com'


@pytest.mark.asyncio
async def test_authenticate_with_google_existing_user_update_provider(monkeypatch):
    fake_idinfo = {
        'aud': 'fake-google-client.apps.googleusercontent.com',
        'sub': 'zxy987654321',
        'email': 'existing@example.com',
        'email_verified': True,
        'name': 'Existing User',
        'given_name': 'Existing',
        'family_name': 'User',
        'picture': 'https://example.com/existing.png'
    }

    monkeypatch.setattr('app.services.auth_service.id_token.verify_oauth2_token', lambda token, request, audience: fake_idinfo)
    monkeypatch.setattr(settings, 'google_client_id', 'fake-google-client.apps.googleusercontent.com')

    async def fake_find_by_email(email):
        return {'id': 'user123', 'email': 'existing@example.com', 'auth_provider': 'email'}

    async def fake_update(user_id, update_dict):
        # Simulate update by returning True
        return True

    async def fake_find_by_id(_id):
        return {'id': 'user123', 'email': 'existing@example.com', 'auth_provider': 'google', 'google_id': 'zxy987654321'}

    monkeypatch.setattr('app.repositories.user_repository.UserRepository.find_by_email', fake_find_by_email)
    monkeypatch.setattr('app.repositories.user_repository.UserRepository.update', fake_update)
    monkeypatch.setattr('app.repositories.user_repository.UserRepository.find_by_id', fake_find_by_id)

    tokens = await AuthService.authenticate_with_google('fake-token')
    assert tokens['user']['email'] == 'existing@example.com'
