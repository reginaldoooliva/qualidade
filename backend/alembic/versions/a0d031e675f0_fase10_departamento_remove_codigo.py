"""fase10_departamento_remove_codigo

Revision ID: a0d031e675f0
Revises: aba4f15bb309
Create Date: 2026-09-24 19:58:49.718795

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0d031e675f0'
down_revision: Union[str, Sequence[str], None] = 'aba4f15bb309'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f('ix_departamentos_codigo'), table_name='departamentos')
    op.drop_column('departamentos', 'codigo')
    op.create_index(op.f('ix_departamentos_nome'), 'departamentos', ['nome'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_departamentos_nome'), table_name='departamentos')
    op.add_column('departamentos', sa.Column('codigo', sa.String(length=60), nullable=True))
    op.execute("UPDATE departamentos SET codigo = nome")
    op.alter_column('departamentos', 'codigo', nullable=False)
    op.create_index(op.f('ix_departamentos_codigo'), 'departamentos', ['codigo'], unique=True)
