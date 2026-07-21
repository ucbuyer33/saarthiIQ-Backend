"""add user_id column (Feistel prefix)

Revision ID: a1b2c3d4e5f6
Revises: 4bb5a850879b
Create Date: 2026-07-19
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '4bb5a850879b'
branch_labels = None
depends_on = None


def upgrade() -> None:
   pass


def downgrade() -> None:
    pass