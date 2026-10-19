from app.core.chat_sessions.workflow import ChatSessionCountWorkflow
from app.database.history_session_repository import HistorySessionRepository
from app.models.history_table import HistoryTable
from app.routes.chat_sessions.controllers.controller import (
    ChatSessionCountController,
)
from app.routes.chat_sessions.services.service import ChatSessionCountService


def get_chat_session_count_controller() -> ChatSessionCountController:
    """Compose the session counting dependencies for the HTTP route.

    Returns:
        Controller configured with the concrete database repository,
        workflow and service.
    """
    repository = HistorySessionRepository(model=HistoryTable)
    workflow = ChatSessionCountWorkflow(repository=repository)
    service = ChatSessionCountService(workflow=workflow)

    return ChatSessionCountController(service=service)