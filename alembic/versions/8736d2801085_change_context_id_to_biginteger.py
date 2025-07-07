"""Change context_id to BigInteger

Revision ID: 8736d2801085
Revises: 43d64137ab50
Create Date: 2025-06-25 22:17:51.566670

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8736d2801085'
down_revision: Union[str, Sequence[str], None] = '43d64137ab50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('contexts', 'context_id', type_=sa.BigInteger())

def downgrade():
    op.alter_column('contexts', 'context_id', type_=sa.Integer())