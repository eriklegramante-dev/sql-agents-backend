import pytest
from fastapi import HTTPException

from app.models.users_table import UserTable
from app.security import security


class FakeAuthenticator:
    def __init__(self, subject):
        self.subject = subject

    def verify_token(self, token: str):
        if isinstance(self.subject, Exception):
            raise self.subject
        return self.subject


class FakeRepository:
    def __init__(self, model):
        self.model = model

    async def get_by_id(self, record_id: int):
        if record_id == 1:
            return UserTable(id=1, email="user@example.com")
        return None


@pytest.mark.asyncio
async def test_get_current_user_returns_user(monkeypatch):
    monkeypatch.setattr(security, "JWTAuthenticator", lambda: FakeAuthenticator(1))
    monkeypatch.setattr(security, "DatabaseRepository", FakeRepository)

    user = await security.get_current_user("token")

    assert user.id == 1


@pytest.mark.asyncio
async def test_get_current_user_rejects_missing_user(monkeypatch):
    monkeypatch.setattr(security, "JWTAuthenticator", lambda: FakeAuthenticator(2))
    monkeypatch.setattr(security, "DatabaseRepository", FakeRepository)

    with pytest.raises(HTTPException) as exc:
        await security.get_current_user("token")

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_rejects_invalid_token(monkeypatch):
    monkeypatch.setattr(
        security, "JWTAuthenticator", lambda: FakeAuthenticator(RuntimeError("bad"))
    )
    monkeypatch.setattr(security, "DatabaseRepository", FakeRepository)

    with pytest.raises(HTTPException) as exc:
        await security.get_current_user("token")

    assert exc.value.status_code == 401
