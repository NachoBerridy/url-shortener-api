"""Nombre a tabla URL

Revision ID: 9fcd345431b0
Revises:
Create Date: 2024-10-07 20:03:27.186676

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "9fcd345431b0"
down_revision = (
    None  # Si tienes migraciones anteriores, asegúrate de poner aquí el ID correcto
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Añadir la columna `name` a la tabla `urls`
    op.add_column("urls", sa.Column("name", sa.String(), nullable=True))


def downgrade() -> None:
    # Eliminar la columna `name` si se revierte la migración
    op.drop_column("urls", "name")
