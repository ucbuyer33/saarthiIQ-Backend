"""merge conflicting heads

Revision ID: ebf249ef94bc
Revises: a1b2c3d4e5f6, add_location_user_sessions
Create Date: 2026-07-19 22:53:03.757740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ebf249ef94bc'
down_revision: Union[str, Sequence[str], None] = ('a1b2c3d4e5f6', 'add_location_user_sessions')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
