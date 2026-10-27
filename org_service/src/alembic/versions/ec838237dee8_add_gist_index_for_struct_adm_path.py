"""add gist index for struct adm path

Revision ID: ec838237dee8
Revises: 4011a7afab42
Create Date: 2026-10-27 17:01:48.417934

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ec838237dee8"
down_revision: str | Sequence[str] | None = "4011a7afab42"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_struct_adm_path_gist",
        "struct_adm",
        ["path"],
        unique=False,
        postgresql_using="gist",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_struct_adm_path_gist",
        table_name="struct_adm",
    )
