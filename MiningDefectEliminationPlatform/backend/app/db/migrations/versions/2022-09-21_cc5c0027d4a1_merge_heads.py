"""merge heads

Revision ID: cc5c0027d4a1
Revises: 6c03a7bfec5b, 383cfe1e8b0f
Create Date: 2022-09-21 23:35:08.387932

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc5c0027d4a1'
down_revision = ('6c03a7bfec5b', '383cfe1e8b0f')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
