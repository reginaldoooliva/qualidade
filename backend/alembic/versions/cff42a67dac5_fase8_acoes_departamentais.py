"""fase8_acoes_departamentais

Revision ID: cff42a67dac5
Revises: 8d98c76a9fe7
Create Date: 2026-09-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cff42a67dac5'
down_revision: Union[str, Sequence[str], None] = '8d98c76a9fe7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('nc_acoes_departamentais',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nc_id', sa.Integer(), nullable=False),
    sa.Column('departamento_id', sa.Integer(), nullable=False),
    sa.Column('descricao', sa.Text(), nullable=False),
    sa.Column('status', sa.Enum('PENDENTE', 'CONCLUIDA', name='status_acao_departamental'), nullable=False),
    sa.Column('observacao_conclusao', sa.Text(), nullable=True),
    sa.Column('criado_por_id', sa.Integer(), nullable=False),
    sa.Column('concluido_por_id', sa.Integer(), nullable=True),
    sa.Column('concluido_em', sa.DateTime(timezone=True), nullable=True),
    sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['nc_id'], ['nao_conformidades.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['departamento_id'], ['departamentos.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['criado_por_id'], ['usuarios.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['concluido_por_id'], ['usuarios.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('nc_acoes_departamentais')
    sa.Enum(name='status_acao_departamental').drop(op.get_bind(), checkfirst=True)
