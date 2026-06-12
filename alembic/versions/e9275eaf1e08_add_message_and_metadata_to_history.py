"""add_message_and_metadata_to_history

Revision ID: e9275eaf1e08
Revises: c39d14216256
Create Date: 2026-06-10 13:50:20.713583

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e9275eaf1e08"  # pragma: allowlist secret
down_revision: Union[str, Sequence[str], None] = "c39d14216256"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "history",
        sa.Column(
            "message",
            sa.Text(),
            nullable=False,
            server_default="",
        ),
    )

    op.add_column(
        "history",
        sa.Column(
            "metadata",
            sa.JSON(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("history", "metadata")

    op.drop_column("history", "message")
