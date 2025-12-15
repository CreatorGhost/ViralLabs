"""Add credits column to users table

Revision ID: b4bf5567358g
Revises: a3ae4456247f
Create Date: 2025-12-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4bf5567358g'
down_revision: Union[str, Sequence[str], None] = 'a3ae4456247f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add credits column to users table."""
    op.add_column('users', sa.Column('credits', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    """Remove credits column from users table."""
    op.drop_column('users', 'credits')
