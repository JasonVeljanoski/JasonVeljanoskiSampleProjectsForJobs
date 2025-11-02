"""threshold--merge

Revision ID: c1cb1365e6cf
Revises: e10dfa326d0e, 94f141577429
Create Date: 2022-12-21 02:19:52.759122

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c1cb1365e6cf"
down_revision = ("e10dfa326d0e", "94f141577429")
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("Dashboard", sa.Column("threshold_5_why", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("Dashboard", "threshold_5_why")
