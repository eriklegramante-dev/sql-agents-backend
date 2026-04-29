# Bootstrap Admin

Use this after starting the stack and applying migrations to create the first admin user in a fresh database.

```bash
docker compose up -d --build
alembic upgrade head
```

Then run this from the project root:

```bash
python3 - <<'PY'
import asyncio
from datetime import date

from sqlalchemy import select

from app.database.repository import DatabaseRepository
from app.models.users_table import UserRole, UserStatus, UserTable
from app.security.hashing import PasswordManager

ADMIN_EMAIL = "bootstrap.admin@example.com"
ADMIN_PASSWORD = "Admin@12345"


async def main() -> None:
    repository = DatabaseRepository(model=UserTable)
    sessionmaker = repository.db_connection.get_session()

    async with sessionmaker() as session:
        result = await session.execute(
            select(UserTable).where(UserTable.email == ADMIN_EMAIL)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"bootstrap_admin_id={existing_user.id}")
            await repository.db_connection.close()
            return

        admin = UserTable(
            name="Bootstrap Admin",
            email=ADMIN_EMAIL,
            cpf="10000000001",
            birth_date=date(1990, 1, 1),
            country="Brazil",
            password=PasswordManager().hash_password(ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )

        session.add(admin)
        await session.commit()
        await session.refresh(admin)

        print(f"bootstrap_admin_id={admin.id}")

    await repository.db_connection.close()


asyncio.run(main())
PY
```

Initial credentials:

```text
email: bootstrap.admin@example.com
password: Admin@12345
```
