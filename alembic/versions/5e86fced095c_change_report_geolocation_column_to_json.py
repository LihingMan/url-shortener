"""change report.geolocation column to json

Revision ID: 5e86fced095c
Revises: 5d87ad0382c7
Create Date: 2024-07-03 16:19:30.327747

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e86fced095c'
down_revision: Union[str, None] = '5d87ad0382c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Manual command to alter the type with a USING clause for conversion
    op.execute("ALTER TABLE reports ALTER COLUMN geolocation TYPE JSON USING geolocation::json")

def downgrade():
    # Convert back to text if necessary
    op.execute("ALTER TABLE reports ALTER COLUMN geolocation TYPE VARCHAR USING geolocation::text")
