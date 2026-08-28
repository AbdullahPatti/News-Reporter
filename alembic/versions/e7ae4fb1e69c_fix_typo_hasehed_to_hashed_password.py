"""fix_typo_hasehed_to_hashed_password

Revision ID: e7ae4fb1e69c
Revises: ee7290117a1a
Create Date: 2026-08-20 01:33:07.351269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7ae4fb1e69c'
down_revision: Union[str, Sequence[str], None] = 'ee7290117a1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename hasehed_password -> hashed_password (typo fix)."""
    op.alter_column('users', 'hasehed_password', new_column_name='hashed_password')


def downgrade() -> None:
    """Rename hashed_password -> hasehed_password (revert typo fix)."""
    op.alter_column('users', 'hashed_password', new_column_name='hasehed_password')
