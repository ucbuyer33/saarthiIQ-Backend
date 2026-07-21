"""drop role column from users (single-role recruiter app)

Revision ID: 7c1a9e2f4b3d
Revises: 4bb5a850879b
Create Date: 2026-07-21 16:12:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c1a9e2f4b3d'
down_revision: Union[str, Sequence[str], None] = '4bb5a850879b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The app is now single-role (recruiter only). Every existing account is
    # treated as a recruiter, so the `role` column is no longer needed.
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('role')


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('role', sa.String(), nullable=True, server_default='recruiter'))
