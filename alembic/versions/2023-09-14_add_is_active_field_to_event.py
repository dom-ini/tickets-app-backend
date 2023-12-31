"""add is_active field to event

Revision ID: 895ca892d8e7
Revises: c15a4c820af7
Create Date: 2023-09-14 19:41:10.910490

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "895ca892d8e7"
down_revision = "c15a4c820af7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("event", sa.Column("is_active", sa.Boolean(), nullable=False))
    op.drop_constraint("passwordresettoken_value_key", "passwordresettoken", type_="unique")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint("passwordresettoken_value_key", "passwordresettoken", ["value"])
    op.drop_column("event", "is_active")
    # ### end Alembic commands ###
