from typing import Optional

from app.routes.delete.user.dtos.dto import DeleteUserRequestDTO
from app.models.users_table import UserTable, UserRole
from app.routes.create.admin.dtos.dto import CreateAdminRequestDTO
from app.routes.create.user.dtos.dto import CreateUserRequestDTO
from app.logs.setup_logger import LoggerManager, LOGGER


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

    def can_view(self, request: object, current_user: UserTable) -> bool:
        # TODO: @Ronald

        pass

    def can_update(self, request: object, current_user: UserTable) -> bool:
        # TODO: @Mouth

        pass

    def can_delete(
        self,
        request: DeleteUserRequestDTO,
        current_user: UserTable,
    ) -> bool:
        """
        Determines whether the current user can delete a user.

        Allows administrators to delete any user and restricts
        standard users to deleting only their own account using
        id, email, or cpf.

        Args:
            request (DeleteUserRequestDTO): DTO containing the user
                identifier used for deletion.
            current_user (UserTable): Authenticated user requesting
                the delete operation.

        Returns:
            bool: True when the deletion is allowed, otherwise False.
        """
        self.logger.log_debug(
            f"[policy] validating delete permission for {request.__class__.__name__}"
        )

        if current_user.role == UserRole.ADMIN:
            self.logger.log_info(
                f"[policy] ADMIN {current_user.id} allowed delete access."
            )
            return True

        if request.id is not None and request.id == current_user.id:
            self.logger.log_info(
                f"[policy] USER {current_user.id} allowed delete by own id."
            )
            return True

        if request.email is not None and request.email == current_user.email:
            self.logger.log_info(
                f"[policy] USER {current_user.id} allowed delete by own email."
            )
            return True

        if request.cpf is not None and request.cpf == current_user.cpf:
            self.logger.log_info(
                f"[policy] USER {current_user.id} allowed delete by own cpf."
            )
            return True

        self.logger.log_info(
            f"[policy] USER {current_user.id} denied delete access."
        )
        return False