"""add unique constraint to habit_logs

Revision ID: 80767903828c
Revises: 80767903828b
Create Date: 2026-01-15 16:50:00
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = '80767903828c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        "uq_habit_log_per_day",
        "habit_logs",
        ["habit_id", "log_date"]
    )


def downgrade():
    op.drop_constraint(
        "uq_habit_log_per_day",
        "habit_logs",
        type_="unique"
    )
