from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '3aa0ce266d69'
down_revision = None  # No previous migration
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('elections', sa.Column('threshold_votes', sa.Integer, nullable=True))

def downgrade():
    op.drop_column('elections', 'threshold_votes')
