"""add user table

Revision ID: dc514e279a1d
Revises: dd4fd7a22c4a
Create Date: 2023-03-17 10:33:40.226142

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'dc514e279a1d'
down_revision = 'dd4fd7a22c4a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('first_name', sa.String(length=256), nullable=False),
                    sa.Column('last_name', sa.String(length=256), nullable=False),
                    sa.Column('telegram_nickname', sa.String(length=256), nullable=False),
                    sa.Column('telegram_chat_id', sa.String(length=256), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
