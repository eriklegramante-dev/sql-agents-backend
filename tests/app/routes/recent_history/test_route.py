import pytest

from app.models.users_table import UserTable
from app.routes.recent_history import route as recent_history_route


pytestmark = pytest.mark.asyncio


class RecentHistoryController:
    def __init__(self):
        self.created = True

    async def get_recent_history(self, current_user):
        return {"current_user": current_user.id}


async def test_recent_history_route_delegates_to_controller(monkeypatch):
    monkeypatch.setattr(
        recent_history_route,
        "RecentHistoryController",
        RecentHistoryController,
    )

    current_user = UserTable(id=8)

    result = await recent_history_route.get_recent_history(current_user)

    assert result == {"current_user": 8}
