"""Change context_id in categories to BigInteger

Revision ID: 19141393ec09
Revises: 8736d2801085
Create Date: 2025-06-25 22:32:28.317960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19141393ec09'
down_revision: Union[str, Sequence[str], None] = '8736d2801085'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('categories', 'context_id', type_=sa.BigInteger())

def downgrade():
    op.alter_column('categories', 'context_id', type_=sa.Integer())
