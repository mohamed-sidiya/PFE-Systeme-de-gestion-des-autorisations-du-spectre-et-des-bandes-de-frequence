"""add payment to factures

Revision ID: 9d0e1f2a3b4c
Revises: 7b9c0d1e2f3a
Create Date: 2026-05-29 15:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "9d0e1f2a3b4c"
down_revision = "7b9c0d1e2f3a"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("factures", schema=None) as batch_op:
        batch_op.add_column(sa.Column("date_paiement", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("payee_par_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_factures_payee_par_id_users",
            "users",
            ["payee_par_id"],
            ["id"],
        )


def downgrade():
    with op.batch_alter_table("factures", schema=None) as batch_op:
        batch_op.drop_constraint("fk_factures_payee_par_id_users", type_="foreignkey")
        batch_op.drop_column("payee_par_id")
        batch_op.drop_column("date_paiement")
