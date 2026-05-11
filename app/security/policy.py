from typing import Optional

from app.models.users_table import UserTable, UserRole
from app.routes.create.admin.dtos.dto import CreateAdminRequestDTO
from app.routes.create.user.dtos.dto import CreateUserRequestDTO
from app.logs.setup_logger import LoggerManager, LOGGER
from app.routes.update.dtos.dto import UpdateUserRequestDTO


class UserPolicy:
    """
    Class responsible for handling user authorization policies.

    This class defines the access control rules that determine whether a user can perform
    specific operations on user data based on their role and the provided request attributes.

    Attributes:
        logger (LoggerManager): Logger instance for recording debug and info events during policy checks.
    """

    def __init__(self, logger: Optional[LoggerManager] = None) -> None:
        self.logger = logger or LOGGER

    def can_create(
        self,
        request: CreateUserRequestDTO | CreateAdminRequestDTO,
        current_user: UserTable,
    ) -> bool:
        """
        Determines whether the current user is allowed to create users.

        Args:
            request (CreateUserRequestDTO | CreateAdminRequestDTO): DTO containing creation data.
            current_user (UserTable): The user attempting to perform the creation.

        Returns:
            bool: True if the user is authorized to create users, False otherwise.
        """
        self.logger.log_debug(
            f"[policy] validating create permission for {request.__class__.__name__}"
        )
        if current_user.role == UserRole.ADMIN:
            self.logger.log_debug(f"[policy] ADMIN {current_user.id} can create users.")
            return True

        self.logger.log_info(f"[policy] User {current_user.id} denied create access.")
        return False

    def can_update(
        self,
        request: UpdateUserRequestDTO,
        current_user: UserTable
        ) -> bool:
        """
        Validates whether the current user can update another user.
        """

        self.logger.log_debug(
            f"[policy] validating update permission for user {current_user.id}"
        )

        if current_user.role == UserRole.ADMIN:
            self.logger.log_info(
                f"[policy] ADMIN {current_user.id} authorized to update users."
            )
            return True

    def can_view(self, request: object, current_user: UserTable) -> bool:
        # TODO: @Ronald

        pass

    def can_update(self, request: object, current_user: UserTable) -> bool:

        if request.id != current_user.id:
            self.logger.log_info(
                f"[policy] user {current_user.id} denied update access."
            )
            return False

        if request.role is not None:
            self.logger.log_info(
                f"[policy] user {current_user.id} attempted role update."
            )
            return False

        if request.status is not None:
            self.logger.log_info(
                f"[policy] user {current_user.id} attempted status update."
            )
            return False

        self.logger.log_info(
            f"[policy] user {current_user.id} authorized to update own profile."
        )

        return True

    def can_delete(self, request: object, current_user: UserTable) -> bool:
        # TODO: @Djhonsons-baby
        pass
