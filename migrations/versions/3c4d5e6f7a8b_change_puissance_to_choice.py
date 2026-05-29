"""change puissance to choice

Revision ID: 3c4d5e6f7a8b
Revises: 8f2c1d9a4b6e
Create Date: 2026-05-29 13:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "3c4d5e6f7a8b"
down_revision = "8f2c1d9a4b6e"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("demandes_autorisation", schema=None) as batch_op:
        batch_op.alter_column(
            "puissance",
            existing_type=sa.Numeric(precision=10, scale=2),
            type_=sa.String(length=20),
            existing_nullable=True,
        )

    op.execute(
        """
        UPDATE demandes_autorisation
        SET puissance = CASE
            WHEN puissance IS NULL OR puissance = '' THEN NULL
            WHEN CAST(puissance AS FLOAT) >= 100 THEN 'haute'
            WHEN CAST(puissance AS FLOAT) >= 10 THEN 'moyenne'
            ELSE 'basse'
        END
        """
    )


def downgrade():
    op.execute(
        """
        UPDATE demandes_autorisation
        SET puissance = CASE
            WHEN puissance = 'haute' THEN '100'
            WHEN puissance = 'moyenne' THEN '10'
            WHEN puissance = 'basse' THEN '1'
            ELSE NULL
        END
        """
    )
    with op.batch_alter_table("demandes_autorisation", schema=None) as batch_op:
        batch_op.alter_column(
            "puissance",
            existing_type=sa.String(length=20),
            type_=sa.Numeric(precision=10, scale=2),
            existing_nullable=True,
        )
