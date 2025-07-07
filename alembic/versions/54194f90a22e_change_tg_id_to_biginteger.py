"""Change tg_id to BigInteger

Revision ID: 54194f90a22e
Revises: 6ded67202ec4
Create Date: 2025-07-01 00:52:53.473296

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '54194f90a22e'
down_revision: Union[str, Sequence[str], None] = '6ded67202ec4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('users', 'tg_id',
        existing_type=sa.INTEGER(),
        type_=sa.BigInteger(),
        existing_nullable=False
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'tg_id',
        existing_type=sa.BigInteger(),
        type_=sa.INTEGER(),
        existing_nullable=False
    )