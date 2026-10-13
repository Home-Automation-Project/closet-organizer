"""Expand itemfrequency enum for filter schedules

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-12
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    # Add new enum values in chronological order of schedule cadence.
    op.execute("ALTER TYPE itemfrequency ADD VALUE IF NOT EXISTS 'QUARTERLY'")
    op.execute("ALTER TYPE itemfrequency ADD VALUE IF NOT EXISTS 'SIX_MONTHS'")
    op.execute("ALTER TYPE itemfrequency ADD VALUE IF NOT EXISTS 'ANNUAL'")


def downgrade() -> None:
    # PostgreSQL enum value removal is destructive and not supported directly.
    pass
