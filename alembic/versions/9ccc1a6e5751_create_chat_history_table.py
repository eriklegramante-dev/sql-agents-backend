"""create chat history table

Revision ID: 9ccc1a6e5751
Revises: 0001_create_users_table
Create Date: 2026-05-22 19:50:54.151552

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9ccc1a6e5751"
down_revision: Union[str, Sequence[str], None] = "0001_create_users_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Creates the chat_history table.
    """

    op.create_table(
        "chat_history",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "message",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """
    Drops the chat_history table.
    """

    op.drop_table("chat_history")
