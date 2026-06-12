from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b8719f4756ce"  # pragma: allowlist secret
down_revision: Union[str, Sequence[str], None] = "523461f2ff3a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        ALTER TABLE history
        ALTER COLUMN message DROP DEFAULT
    """)

    op.execute("""
        UPDATE history
        SET message = '"{}"'
        WHERE message IS NULL OR trim(message) = ''
    """)

    op.execute("""
        UPDATE history
        SET message = to_json(message)::text
        WHERE message <> '"{}"'
    """)

    op.alter_column(
        "history",
        "message",
        type_=sa.JSON(),
        postgresql_using="message::json",
    )


def downgrade():
    op.alter_column(
        "history",
        "message",
        type_=sa.Text(),
        postgresql_using="message::text",
    )

    op.execute("""
        ALTER TABLE history
        ALTER COLUMN message SET DEFAULT ''
    """)
