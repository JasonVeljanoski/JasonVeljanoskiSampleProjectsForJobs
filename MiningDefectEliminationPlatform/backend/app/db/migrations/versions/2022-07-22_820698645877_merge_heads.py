"""merge heads

Revision ID: 820698645877
Revises: fb7883226067, dba30cfa3503
Create Date: 2022-07-22 08:19:43.046537

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '820698645877'
down_revision = ('fb7883226067', 'dba30cfa3503')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
