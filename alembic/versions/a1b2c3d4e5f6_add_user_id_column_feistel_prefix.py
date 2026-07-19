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
    # Add nullable user_id column first (existing rows get NULL)
    op.add_column(
        'users',
        sa.Column('user_id', sa.String(length=8), nullable=True),
    )
    op.execute("""
        UPDATE users
        SET user_id = CASE
            WHEN role = 'recruiter'   THEN 'RC' || LPAD(CAST((MOD(CAST(id AS NUMERIC) * 6364136223846793005 + 1442695040888963407, 1000000)) AS TEXT), 6, '0')
            WHEN role = 'interviewer' THEN 'IV' || LPAD(CAST((MOD(CAST(id AS NUMERIC) * 6364136223846793005 + 1442695040888963407, 1000000)) AS TEXT), 6, '0')
            ELSE                           'US' || LPAD(CAST((MOD(CAST(id AS NUMERIC) * 6364136223846793005 + 1442695040888963407, 1000000)) AS TEXT), 6, '0')
        END
        WHERE user_id IS NULL;
    """)
    # Unique index — enforced by DB, not just SQLAlchemy
    op.create_index(
        op.f('ix_users_user_id'),
        'users',
        ['user_id'],
        unique=True,
    )
    # ── Backfill existing rows ────────────────────────────────────────────────
    # We inline a pure-SQL Feistel so the migration is self-contained and
    # has no Python import dependencies.
    # Strategy: role_prefix || lpad(((id * 6364136223846793005 + 1442695040888963407) % 1000000)::text, 6, '0')
    # This is a simple LCG (not the full Feistel) — good enough for backfill;
    # new registrations use the real Feistel from app/utils/id_gen.py.
    op.execute("""
        UPDATE users
        SET user_id = CASE
            WHEN role = 'recruiter'   THEN 'RC' || LPAD(CAST(((id * 6364136223846793005 + 1442695040888963407) % 1000000) AS TEXT), 6, '0')
            WHEN role = 'interviewer' THEN 'IV' || LPAD(CAST(((id * 6364136223846793005 + 1442695040888963407) % 1000000) AS TEXT), 6, '0')
            WHEN role = 'admin'       THEN 'AD' || LPAD(CAST(((id * 6364136223846793005 + 1442695040888963407) % 1000000) AS TEXT), 6, '0')
            ELSE                           'CD' || LPAD(CAST(((id * 6364136223846793005 + 1442695040888963407) % 1000000) AS TEXT), 6, '0')
        END
        WHERE user_id IS NULL;
    """)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_column('users', 'user_id')
