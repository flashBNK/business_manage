"""added failed_message"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "8be83820bd24"
down_revision: str | Sequence[str] | None = "5c503ece2616"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "failed_message",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("consumer_name", sa.String(length=127), nullable=False),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column("partition", sa.Integer(), nullable=False),
        sa.Column("offset", sa.BigInteger(), nullable=False),
        sa.Column("raw_value", postgresql.BYTEA(), nullable=True),
        sa.Column("raw_key", postgresql.BYTEA(), nullable=True),
        sa.Column("headers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=True),
        sa.Column("correlation_id", sa.Uuid(), nullable=True),
        sa.Column("error_type", sa.Text(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "resolved", "discarded", name="failedmessagestatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("consumer_name", "topic", "partition", "offset", name="unique_failed_kafka_message"),
    )
    op.create_index(op.f("ix_failed_message_correlation_id"), "failed_message", ["correlation_id"], unique=False)
    op.create_index(op.f("ix_failed_message_event_id"), "failed_message", ["event_id"], unique=False)
    op.create_index(op.f("ix_failed_message_status"), "failed_message", ["status"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_failed_message_status"), table_name="failed_message")
    op.drop_index(op.f("ix_failed_message_event_id"), table_name="failed_message")
    op.drop_index(op.f("ix_failed_message_correlation_id"), table_name="failed_message")
    op.drop_table("failed_message")
