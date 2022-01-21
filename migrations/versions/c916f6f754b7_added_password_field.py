"""added password field

Revision ID: c916f6f754b7
Revises: 10c7d0fb2e1e
Create Date: 2022-01-19 17:01:57.116051

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c916f6f754b7'
down_revision = '10c7d0fb2e1e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password_hash', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'password_hash')
    # ### end Alembic commands ###
