"""add unpublished outbox indexes

Revision ID: 4b641fc1156a
Revises: ec838237dee8
Create Date: 2026-10-27 17:35:03.229891

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4b641fc1156a"
down_revision: str | Sequence[str] | None = "ec838237dee8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_outbox_unpublished_occurred_event",
        "outbox_event",
        ["occurred_at", "event_id"],
        unique=False,
        postgresql_where=sa.text("published_at IS NULL"),
    )
    op.create_index(
        "ix_outbox_unpublished_aggregate_occurred_event",
        "outbox_event",
        ["aggregate_id", "occurred_at", "event_id"],
        unique=False,
        postgresql_where=sa.text("published_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "ix_outbox_unpublished_aggregate_occurred_event",
        table_name="outbox_event",
    )
    op.drop_index(
        "ix_outbox_unpublished_occurred_event",
        table_name="outbox_event",
    )
