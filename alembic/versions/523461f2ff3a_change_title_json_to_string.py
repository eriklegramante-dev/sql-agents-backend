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


def upgrade() -> None:
    op.alter_column(
        "history",
        "title",
        existing_type=sa.JSON(),
        type_=sa.String(),
        existing_nullable=False,
        postgresql_using="title::text",
    )


def downgrade() -> None:
    op.alter_column(
        "history",
        "title",
        existing_type=sa.String(),
        type_=sa.JSON(),
        existing_nullable=False,
        postgresql_using="title::json",
    )
