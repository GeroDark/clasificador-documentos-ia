"""merge auth and jobs heads

Revision ID: d1b6c9f4a2e0
Revises: af5cbd73d6e3, cf3e7c1a9d21
Create Date: 2026-04-13 00:10:00.000000

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "d1b6c9f4a2e0"
down_revision: Union[str, Sequence[str], None] = ("af5cbd73d6e3", "cf3e7c1a9d21")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
