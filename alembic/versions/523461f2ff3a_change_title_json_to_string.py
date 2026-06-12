"""change_title_json_to_string

Revision ID: 523461f2ff3a
Revises: e9275eaf1e08
Create Date: 2026-06-10 13:59:48.193772

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "523461f2ff3a"
down_revision: Union[str, Sequence[str], None] = "e9275eaf1e08"
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
