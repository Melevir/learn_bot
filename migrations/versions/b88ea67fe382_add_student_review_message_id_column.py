"""add student review message id column

Revision ID: b88ea67fe382
Revises: a9e1612b5757
Create Date: 2023-06-08 07:01:21.422640

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b88ea67fe382'
down_revision = 'a9e1612b5757'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('assignment', sa.Column('review_message_id_in_student_chat', sa.String(length=512), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('assignment', 'review_message_id_in_student_chat')
    # ### end Alembic commands ###
