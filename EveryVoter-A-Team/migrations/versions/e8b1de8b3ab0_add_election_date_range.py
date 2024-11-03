"""add election date range

Revision ID: e8b1de8b3ab0
Revises: 5560acda1258
Create Date: 2024-10-31 21:23:27.230123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8b1de8b3ab0'
down_revision = '5560acda1258'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('elections', schema=None) as batch_op:
        batch_op.add_column(sa.Column('start_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('end_date', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('elections', schema=None) as batch_op:
        batch_op.drop_column('end_date')
        batch_op.drop_column('start_date')

    # ### end Alembic commands ###