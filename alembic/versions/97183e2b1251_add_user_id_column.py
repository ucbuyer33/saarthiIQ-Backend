"""add user_id column

Revision ID: 97183e2b1251
Revises: ebf249ef94bc
Create Date: 2026-07-19 23:49:47.044340

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '97183e2b1251'
down_revision: Union[str, Sequence[str], None] = 'ebf249ef94bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema. (Skipped because a1b2c3d4e5f6 already added the column)"""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
