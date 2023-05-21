"""make active plays nullable

Revision ID: 7de96aea0f36
Revises: 7bf5a873f2bc
Create Date: 2023-03-22 08:29:36.679604

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '7de96aea0f36'
down_revision = '7bf5a873f2bc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'active_screenplay_id',
                    existing_type=sa.VARCHAR(length=256),
                    nullable=True)
    op.alter_column('user', 'active_act_id',
                    existing_type=sa.VARCHAR(length=256),
                    nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'active_act_id',
                    existing_type=sa.VARCHAR(length=256),
                    nullable=False)
    op.alter_column('user', 'active_screenplay_id',
                    existing_type=sa.VARCHAR(length=256),
                    nullable=False)
    # ### end Alembic commands ###
