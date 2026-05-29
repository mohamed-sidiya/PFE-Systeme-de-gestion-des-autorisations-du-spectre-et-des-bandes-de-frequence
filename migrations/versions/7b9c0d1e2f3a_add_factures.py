"""add factures

Revision ID: 7b9c0d1e2f3a
Revises: 3c4d5e6f7a8b
Create Date: 2026-05-29 15:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "7b9c0d1e2f3a"
down_revision = "3c4d5e6f7a8b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "factures",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("numero_facture", sa.String(length=100), nullable=False),
        sa.Column("demande_id", sa.Integer(), nullable=False),
        sa.Column("creee_par_id", sa.Integer(), nullable=True),
        sa.Column("designation", sa.String(length=255), nullable=False),
        sa.Column("periode_mois", sa.Integer(), nullable=False),
        sa.Column("prix_unitaire", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("montant_ht", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("taux_taxe", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("montant_taxe", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("montant_ttc", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("statut", sa.String(length=50), nullable=False),
        sa.Column("date_creation", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["creee_par_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["demande_id"], ["demandes_autorisation.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("demande_id"),
    )
    with op.batch_alter_table("factures", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_factures_numero_facture"), ["numero_facture"], unique=True)


def downgrade():
    with op.batch_alter_table("factures", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_factures_numero_facture"))
    op.drop_table("factures")
