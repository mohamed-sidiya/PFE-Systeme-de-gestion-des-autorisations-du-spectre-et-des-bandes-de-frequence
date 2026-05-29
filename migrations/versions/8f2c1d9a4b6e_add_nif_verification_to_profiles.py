"""add nif verification to profiles

Revision ID: 8f2c1d9a4b6e
Revises: d4b7bf58a70b
Create Date: 2026-05-29 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8f2c1d9a4b6e"
down_revision = "d4b7bf58a70b"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("profils_utilisateurs", schema=None) as batch_op:
        batch_op.add_column(sa.Column("nif_verifie", sa.Boolean(), server_default=sa.false(), nullable=False))
        batch_op.add_column(sa.Column("nif_verifie_par_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("date_verification_nif", sa.DateTime(), nullable=True))
        batch_op.create_foreign_key(
            "fk_profils_utilisateurs_nif_verifie_par_id_users",
            "users",
            ["nif_verifie_par_id"],
            ["id"],
        )

    with op.batch_alter_table("profils_utilisateurs", schema=None) as batch_op:
        batch_op.alter_column("nif_verifie", server_default=None)


def downgrade():
    with op.batch_alter_table("profils_utilisateurs", schema=None) as batch_op:
        batch_op.drop_constraint("fk_profils_utilisateurs_nif_verifie_par_id_users", type_="foreignkey")
        batch_op.drop_column("date_verification_nif")
        batch_op.drop_column("nif_verifie_par_id")
        batch_op.drop_column("nif_verifie")
