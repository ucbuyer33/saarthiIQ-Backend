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
    """Upgrade schema."""
    # Add user_id column
    op.add_column('users', sa.Column('user_id', sa.String(length=8), nullable=True))
    
    # Backfill existing users with generated IDs
    op.execute("""
        UPDATE users
        SET user_id = CASE
            WHEN role = 'recruiter' THEN 'RC' || LPAD(CAST(((id * 6364136223846793005 + 1442695040888963407) % 1000000) AS TEXT), 6, '0')
            WHEN role = 'admin' THEN 'AD' || LPAD(CAST(((id * 6364136223846793005 + 1442695040888963407) % 1000000) AS TEXT), 6, '0')
            ELSE 'CD' || LPAD(CAST(((id * 6364136223846793005 + 1442695040888963407) % 1000000) AS TEXT), 6, '0')
        END
        WHERE user_id IS NULL;
    """)
    
    # Make column NOT NULL and add unique index
    op.alter_column('users', 'user_id', nullable=False)
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_column('users', 'user_id')