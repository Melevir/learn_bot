"""make message unlimited len

Revision ID: 6fe8a64962a0
Revises: f1af451f96eb
Create Date: 2023-05-18 09:48:24.166561

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '6fe8a64962a0'
down_revision = 'f1af451f96eb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat_message', sa.Column('message', sa.Text(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chat_message', 'message')
    # ### end Alembic commands ###
