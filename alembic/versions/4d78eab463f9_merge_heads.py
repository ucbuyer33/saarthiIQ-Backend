"""merge heads

Revision ID: 4d78eab463f9
Revises: 75188083967d, 97183e2b1251
Create Date: 2026-07-21 19:55:07.055018

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d78eab463f9'
down_revision: Union[str, Sequence[str], None] = ('75188083967d', '97183e2b1251')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
