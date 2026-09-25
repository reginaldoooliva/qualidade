"""fase9_deposito_qualidade

Revision ID: cf2c74038cd1
Revises: 13d0c0a982df
Create Date: 2026-09-22 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf2c74038cd1'
down_revision: Union[str, Sequence[str], None] = '13d0c0a982df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('bloqueios_deposito',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('peca_id', sa.Integer(), nullable=False),
    sa.Column('nao_conformidade_id', sa.Integer(), nullable=True),
    sa.Column('motivo', sa.Text(), nullable=False),
    sa.Column('caracteristica_atencao', sa.Text(), nullable=True),
    sa.Column('cliente', sa.String(length=200), nullable=True),
    sa.Column('status', sa.Enum('BLOQUEADO', 'LIBERADO', name='status_bloqueio_deposito'), nullable=False),
    sa.Column('criado_por_id', sa.Integer(), nullable=False),
    sa.Column('liberado_por_id', sa.Integer(), nullable=True),
    sa.Column('data_liberacao', sa.DateTime(), nullable=True),
    sa.Column('observacao_liberacao', sa.Text(), nullable=True),
    sa.Column('foto_conteudo', sa.LargeBinary(), nullable=True),
    sa.Column('foto_nome_arquivo', sa.String(length=255), nullable=True),
    sa.Column('foto_content_type', sa.String(length=100), nullable=True),
    sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['peca_id'], ['pecas.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['nao_conformidade_id'], ['nao_conformidades.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['criado_por_id'], ['usuarios.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['liberado_por_id'], ['usuarios.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bloqueios_deposito_peca_id'), 'bloqueios_deposito', ['peca_id'], unique=False)
    op.create_index(op.f('ix_bloqueios_deposito_status'), 'bloqueios_deposito', ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_bloqueios_deposito_status'), table_name='bloqueios_deposito')
    op.drop_index(op.f('ix_bloqueios_deposito_peca_id'), table_name='bloqueios_deposito')
    op.drop_table('bloqueios_deposito')
    sa.Enum(name='status_bloqueio_deposito').drop(op.get_bind(), checkfirst=True)
