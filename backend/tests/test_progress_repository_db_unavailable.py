import pytest
import asyncio
from app.repositories.progress_repository import ProgressRepository
from app.database import db


@pytest.mark.asyncio
async def test_find_by_user_database_unavailable(monkeypatch):
    # Ensure db.database is None to simulate unavailable DB
    monkeypatch.setattr(db, 'database', None)

    with pytest.raises(ConnectionError):
        await ProgressRepository.find_by_user('some-user-id', limit=10)
