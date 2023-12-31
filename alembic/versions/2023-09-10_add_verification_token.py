"""add verification token

Revision ID: c15a4c820af7
Revises: 8ef5d44c6c71
Create Date: 2023-09-10 09:03:27.787513

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "c15a4c820af7"
down_revision = "8ef5d44c6c71"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "verificationtoken",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_verificationtoken_id"), "verificationtoken", ["id"], unique=False)
    op.create_index(op.f("ix_verificationtoken_value"), "verificationtoken", ["value"], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_verificationtoken_value"), table_name="verificationtoken")
    op.drop_index(op.f("ix_verificationtoken_id"), table_name="verificationtoken")
    op.drop_table("verificationtoken")
    # ### end Alembic commands ###
