"""fix_none_string_description

Revision ID: d4e6f8a0b1c3
Revises: c3d5e7f9a0b2
Create Date: 2026-06-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = 'd4e6f8a0b1c3'
down_revision: Union[str, None] = 'c3d5e7f9a0b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE events SET description = NULL WHERE description = 'None'")


def downgrade() -> None:
    pass
