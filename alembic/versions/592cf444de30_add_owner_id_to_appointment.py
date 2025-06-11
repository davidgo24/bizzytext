"""add owner_id to appointment

Revision ID: 592cf444de30
Revises: 1f74ad2634ad
Create Date: 2025-06-10 20:52:04.931652
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel  # Ensure this import exists if using sqlmodel types

# revision identifiers, used by Alembic.
revision: str = '592cf444de30'
down_revision: Union[str, None] = '1f74ad2634ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Step 1: Backfill existing null values in appointment.owner_id
    op.execute("UPDATE appointment SET owner_id = 1 WHERE owner_id IS NULL")

    # Step 2: Alter owner_id to NOT NULL
    op.alter_column(
        'appointment', 'owner_id',
        existing_type=sa.INTEGER(),
        nullable=False
    )

    # Optional: Adjust other fields
    op.alter_column(
        'conversationstate', 'booking_complete',
        existing_type=sa.BOOLEAN(),
        nullable=False,
        existing_server_default=sa.text('false')
    )

    op.alter_column(
        'conversationstate', 'offered_slots',
        existing_type=sa.TEXT(),
        type_=sqlmodel.sql.sqltypes.AutoString(),
        existing_nullable=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'conversationstate', 'offered_slots',
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        type_=sa.TEXT(),
        existing_nullable=True
    )

    op.alter_column(
        'conversationstate', 'booking_complete',
        existing_type=sa.BOOLEAN(),
        nullable=True,
        existing_server_default=sa.text('false')
    )

    op.alter_column(
        'appointment', 'owner_id',
        existing_type=sa.INTEGER(),
        nullable=True
    )

