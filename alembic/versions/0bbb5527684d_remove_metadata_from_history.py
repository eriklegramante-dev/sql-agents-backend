"""remove_metadata_from_history

Revision ID: 0bbb5527684d
Revises: b8719f4756ce
Create Date: 2026-06-10 19:52:11.464504

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0bbb5527684d"  # pragma: allowlist secretdown_revision: Union[str, Sequence[str], None] = "b8719f4756ce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_column(
        "history",
        "metadata",
    )


def downgrade():
    op.add_column(
        "history",
        sa.Column(
            "metadata",
            sa.JSON(),
            nullable=True,
        ),
    )
