"""Add optional history sessions, preserving legacy NULL session IDs."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "b23a9d540e02"
down_revision = "a12f8c439d01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("history", sa.Column("session_id", UUID(as_uuid=True), nullable=True))
    op.create_unique_constraint("uq_history_user_session", "history", ["user_id", "session_id"])


def downgrade() -> None:
    op.drop_constraint("uq_history_user_session", "history", type_="unique")
    op.drop_column("history", "session_id")
