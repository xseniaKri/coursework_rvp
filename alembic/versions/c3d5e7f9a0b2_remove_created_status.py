"""remove_created_status

Revision ID: c3d5e7f9a0b2
Revises: b2c4d6e8f0a1
Create Date: 2026-06-06 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d5e7f9a0b2'
down_revision: Union[str, None] = 'b2c4d6e8f0a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_VALS = ('ON_APPROVAL', 'APPROVED', 'REJECTED', 'PLANNED', 'COMPLETED')
OLD_VALS = ('CREATED',) + NEW_VALS


def upgrade() -> None:
    conn = op.get_bind()

    # Переводим существующие CREATED-записи в ON_APPROVAL
    conn.execute(sa.text("UPDATE events SET status = 'ON_APPROVAL' WHERE status = 'CREATED'"))
    conn.execute(sa.text("UPDATE event_history SET old_status = 'ON_APPROVAL' WHERE old_status = 'CREATED'"))
    conn.execute(sa.text("UPDATE event_history SET new_status = 'ON_APPROVAL' WHERE new_status = 'CREATED'"))

    # Пересоздаём enum без CREATED
    # PostgreSQL не поддерживает удаление значений enum напрямую
    conn.execute(sa.text("ALTER TYPE event_status RENAME TO event_status_old"))
    conn.execute(sa.text(
        "CREATE TYPE event_status AS ENUM ('ON_APPROVAL', 'APPROVED', 'REJECTED', 'PLANNED', 'COMPLETED')"
    ))

    conn.execute(sa.text(
        "ALTER TABLE events ALTER COLUMN status TYPE event_status "
        "USING status::text::event_status"
    ))
    conn.execute(sa.text(
        "ALTER TABLE event_history ALTER COLUMN old_status TYPE event_status "
        "USING old_status::text::event_status"
    ))
    conn.execute(sa.text(
        "ALTER TABLE event_history ALTER COLUMN new_status TYPE event_status "
        "USING new_status::text::event_status"
    ))

    conn.execute(sa.text("DROP TYPE event_status_old"))


def downgrade() -> None:
    conn = op.get_bind()

    conn.execute(sa.text("ALTER TYPE event_status RENAME TO event_status_old"))
    conn.execute(sa.text(
        "CREATE TYPE event_status AS ENUM ('CREATED', 'ON_APPROVAL', 'APPROVED', 'REJECTED', 'PLANNED', 'COMPLETED')"
    ))

    conn.execute(sa.text(
        "ALTER TABLE events ALTER COLUMN status TYPE event_status "
        "USING status::text::event_status"
    ))
    conn.execute(sa.text(
        "ALTER TABLE event_history ALTER COLUMN old_status TYPE event_status "
        "USING old_status::text::event_status"
    ))
    conn.execute(sa.text(
        "ALTER TABLE event_history ALTER COLUMN new_status TYPE event_status "
        "USING new_status::text::event_status"
    ))

    conn.execute(sa.text("DROP TYPE event_status_old"))
