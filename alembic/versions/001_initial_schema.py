"""initial schema: equation_systems and solution_methods

Revision ID: 001_initial
Revises: None
Create Date: 2026-03-15

Creates both tables from scratch. Use for fresh installs.
For an existing DB that already has these tables, run:
  python -m alembic stamp head
to mark the DB as up-to-date without running this migration.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "equation_systems",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("variables", sa.JSON(), nullable=False),
        sa.Column("equation1", sa.JSON(), nullable=False),
        sa.Column("equation2", sa.JSON(), nullable=False),
        sa.Column("equation_hash", sa.String(), index=True),
        sa.Column("system_hash", sa.String(), unique=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "solution_methods",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("system_id", sa.Integer(), sa.ForeignKey("equation_systems.id"), nullable=False),
        sa.Column("method_name", sa.String(), nullable=True),
        sa.Column("latex_detailed", sa.String(), nullable=True),
        sa.Column("latex_medium", sa.String(), nullable=True),
        sa.Column("latex_short", sa.String(), nullable=True),
        sa.Column("solution_json", sa.JSON(), nullable=True),
        sa.Column("graph_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("solution_methods")
    op.drop_table("equation_systems")
