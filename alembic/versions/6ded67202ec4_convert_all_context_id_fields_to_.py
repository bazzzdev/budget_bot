"""Convert all context_id fields to BigInteger

Revision ID: 6ded67202ec4
Revises: 19141393ec09
Create Date: 2025-06-25 22:35:22.120881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ded67202ec4'
down_revision: Union[str, Sequence[str], None] = '19141393ec09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # contexts.context_id
    op.alter_column('contexts', 'context_id', type_=sa.BigInteger())

    # categories.context_id
    op.alter_column('categories', 'context_id', type_=sa.BigInteger())

    # expenses.context_id
    op.alter_column('expenses', 'context_id', type_=sa.BigInteger())

    # incomes.context_id
    op.alter_column('incomes', 'context_id', type_=sa.BigInteger())


def downgrade():
    # downgrade обратно в Integer (необязательно, но полезно для откатов)
    op.alter_column('contexts', 'context_id', type_=sa.Integer())
    op.alter_column('categories', 'context_id', type_=sa.Integer())
    op.alter_column('expenses', 'context_id', type_=sa.Integer())
    op.alter_column('incomes', 'context_id', type_=sa.Integer())
