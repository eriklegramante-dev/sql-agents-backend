from app.core.chat_sessions.workflow import ChatSessionCountWorkflow
from app.routes.chat_sessions.dtos.dto import (
    ChatSessionCountDataDTO,
    ChatSessionCountResponseDTO,
)


class ChatSessionCountService:
    """
    Service responsible for handling saved session count requests.

    Delegates session counting to the workflow and converts the total
    into a standardized response DTO.

    Attributes:
        workflow (ChatSessionCountWorkflow):
            Workflow responsible for retrieving the user's session total.
    """

    def __init__(
        self,
        workflow: ChatSessionCountWorkflow | None = None,
    ) -> None:
        """
        Initialize service dependencies.

        Args:
            workflow (ChatSessionCountWorkflow | None):
                Optional workflow instance for dependency injection.
                Defaults to ChatSessionCountWorkflow.
        """
        self.workflow = (
            workflow if workflow is not None else ChatSessionCountWorkflow()
        )

    async def execute(self, user_id: int) -> ChatSessionCountResponseDTO:
        """
        Retrieve and format the authenticated user's saved session total.

        Args:
            user_id (int):
                Authenticated user identifier used to filter sessions.

        Returns:
            ChatSessionCountResponseDTO:
                Successful response containing the saved session total,
                including zero when no matching sessions exist.

        Raises:
            SQLAlchemyError:
                If session counting fails in the workflow.
        """
        total = await self.workflow.execute(user_id=user_id)

        return ChatSessionCountResponseDTO(
            success=True,
            message="Chat sessions counted successfully.",
            data=ChatSessionCountDataDTO(total=total),
        )