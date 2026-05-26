from typing import Optional

from app.models.users_table import UserTable, UserRole
from app.routes.create.admin.dtos.dto import CreateAdminRequestDTO
from app.routes.create.user.dtos.dto import CreateUserRequestDTO
from app.logs.setup_logger import LoggerManager, LOGGER
from app.routes.read.dtos.dto import GetUserRequestDTO

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
            self.logger.log_debug(
                f"[policy] ADMIN {current_user.id} can create users."
            )
            return True

        self.logger.log_info(f"[policy] User {current_user.id} denied create access.")
        return False

    def can_view(
            self, 
            request: GetUserRequestDTO, 
            current_user: UserTable
    ) -> bool:
        
        self.logger.log_debug(
            f"[policy] validating view permission" 
            f"for user {current_user.id}"
        )

        if current_user.role == UserRole.ADMIN:

            self.logger.log_info(
                f"[policy] ADMIN {current_user.id}" 
                f"authorized to view users."
            )

            return True
        
        forbidden_filters = [
            request.email,
            request.name,
            request.cpf,
            request.country,
            request.role,
            request.status
        ]

        has_forbidden_filters = any(
            value is not None for value in forbidden_filters
        )  

        if has_forbidden_filters:

            self.logger.log_info(
                f"[policy] Access denied for user"
                f"{current_user.id}: forbidden filters."
            )

            return False

        if request.id is None:

            self.logger.log_info(
                f"[policy] User {current_user.id}"
                f"authorized to view own profile"
            )

            return True

        if request.id == current_user.id:

            self.logger.log_info(
                f"[policy] User {current_user.id}"
                f"authorized to view own profile by id"
            )

            return True
        
        self.logger.log_info(
            f"[policy] Access denied for user "
            f"{current_user.id}: attempted access" 
            f"to user {request.id}."
        )

        return False

    def can_update(self, request: object, current_user: UserTable) -> bool:

        #TODO: @Mouth

        pass

    def can_delete(self, request: object, current_user: UserTable) -> bool:

        #TODO: @Djhonsons-baby

        pass
