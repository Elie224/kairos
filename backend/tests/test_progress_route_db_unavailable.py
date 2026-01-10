from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.utils.permissions import get_current_user
from app.database import db


@pytest.fixture(autouse=True)
def disable_db_connection(monkeypatch):
    # Simulate DB not connected
    monkeypatch.setattr(db, 'database', None)


async def fake_user():
    return {"id": "test-user"}


def test_get_user_progress_returns_503_when_db_unavailable(monkeypatch):
    # Override dependency to inject authenticated user
    app.dependency_overrides[get_current_user] = fake_user

    client = TestClient(app)
    response = client.get('/api/progress')
    assert response.status_code == 503
    assert 'Service temporairement indisponible' in response.json().get('detail', '')
