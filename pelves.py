import asyncio
import sys
from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import DatabaseConnection
from app.models.users_table import UserRole, UserStatus, UserTable
from app.routes.create.admin.dtos.dto import CreateAdminRequestDTO
from app.security.hashing import PasswordManager


ADMIN_NAME = "Bootstrap Admin"
ADMIN_EMAIL = "bootstrap.admin@example.com"
ADMIN_CPF = "00000000001"
ADMIN_BIRTH_DATE = date(1990, 1, 1)
ADMIN_COUNTRY = "Brazil"
ADMIN_PASSWORD = "MyStr0ngP@ssw0rd!"
ALLOW_EXISTING_USERS = True 


def build_request() -> CreateAdminRequestDTO:
    return CreateAdminRequestDTO(
        name=ADMIN_NAME,
        email=ADMIN_EMAIL,
        cpf=ADMIN_CPF,
        birth_date=ADMIN_BIRTH_DATE,
        country=ADMIN_COUNTRY,
        password=ADMIN_PASSWORD,
    )


async def create_admin(
    request: CreateAdminRequestDTO,
    allow_existing_users: bool,
) -> int:

    print("\n[DEBUG] Starting admin creation process...")

    connection = DatabaseConnection()

    print("[DEBUG] DatabaseConnection created")

    sessionmaker = connection.get_session()

    print("[DEBUG] Sessionmaker created")

    try:
        async with sessionmaker() as session:

            print("[DEBUG] Database session opened")

            total_users = await session.scalar(
                select(func.count(UserTable.id))
            )

            print(f"[DEBUG] Total users in database: {total_users}")

            if total_users and not allow_existing_users:

                print(
                    "[DEBUG] Users already exist and "
                    "ALLOW_EXISTING_USERS=False"
                )

                raise ValueError(
                    "Users table is not empty. "
                    "Set ALLOW_EXISTING_USERS=True to override."
                )

            existing_user = await session.scalar(
                select(UserTable).where(
                    or_(
                        UserTable.email == str(request.email),
                        UserTable.cpf == request.cpf,
                    )
                )
            )

            print(f"[DEBUG] Existing user found: {existing_user}")

            if existing_user:
                raise ValueError(
                    "A user with this email or CPF already exists."
                )

            hashed_password = PasswordManager().hash_password(
                request.password
            )

            print(f"[DEBUG] Password hashed successfully")

            admin = UserTable(
                name=request.name,
                email=str(request.email),
                cpf=request.cpf,
                birth_date=request.birth_date,
                password=hashed_password,
                country=request.country,
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
            )

            print("[DEBUG] Admin object created")

            session.add(admin)

            print("[DEBUG] Admin added to session")

            await session.commit()

            print("[DEBUG] COMMIT EXECUTED SUCCESSFULLY")

            await session.refresh(admin)

            print("[DEBUG] Admin refreshed from database")

            print(
                f"[DEBUG] Created admin -> "
                f"id={admin.id}, "
                f"email={admin.email}"
            )

            users = await session.execute(select(UserTable))

            print("\n[DEBUG] ALL USERS IN DATABASE:")

            all_users = users.scalars().all()

            for user in all_users:
                print(
                    f"-> id={user.id}, "
                    f"name={user.name}, "
                    f"email={user.email}, "
                    f"role={user.role}"
                )

            return int(admin.id)

    except SQLAlchemyError as exc:

        print(f"\n[DEBUG] SQLAlchemyError: {exc}")

        raise RuntimeError(
            f"Database error while creating admin: {exc}"
        ) from exc

    except Exception as exc:

        print(f"\n[DEBUG] General exception: {exc}")

        raise

    finally:

        print("\n[DEBUG] Closing database connection...")

        await connection.close()

        print("[DEBUG] Database connection closed")


async def main() -> int:

    print("\n[DEBUG] Running main()")

    try:

        request = build_request()

        print(f"[DEBUG] Request DTO created: {request}")

        admin_id = await create_admin(
            request,
            ALLOW_EXISTING_USERS
        )

    except Exception as exc:

        print(
            f"\nFailed to create initial admin: {exc}",
            file=sys.stderr
        )

        return 1

    print(
        f"\nInitial admin created successfully. "
        f"id={admin_id} "
        f"email={request.email}"
    )

    return 0


if __name__ == "__main__":

    print("[DEBUG] Script execution started")

    raise SystemExit(asyncio.run(main()))