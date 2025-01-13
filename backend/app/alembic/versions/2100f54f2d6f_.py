"""empty message

Revision ID: 2100f54f2d6f
Revises: 70e21a657190, 9db8787d7e44
Create Date: 2025-01-12 23:38:13.172240

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '2100f54f2d6f'
down_revision = ('70e21a657190', '9db8787d7e44')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
