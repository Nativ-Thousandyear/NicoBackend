"""Add threshold_votes column to elections

Revision ID: f106f96af512
Revises: 
Create Date: 2024-11-02 08:56:01.465509

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f106f96af512'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('elections', schema=None) as batch_op:
        batch_op.add_column(sa.Column('threshold_votes', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('elections', schema=None) as batch_op:
        batch_op.drop_column('threshold_votes')

    # ### end Alembic commands ###