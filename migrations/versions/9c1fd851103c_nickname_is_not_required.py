"""nickname is not required

Revision ID: 9c1fd851103c
Revises: 7cb63055cd27
Create Date: 2023-05-16 16:17:28.935490

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c1fd851103c'
down_revision = '7cb63055cd27'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'telegram_nickname',
               existing_type=sa.VARCHAR(length=256),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'telegram_nickname',
               existing_type=sa.VARCHAR(length=256),
               nullable=False)
    # ### end Alembic commands ###
