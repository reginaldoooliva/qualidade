"""fase7_rnc_tipo_fornecedor_maquina_departamento_fotos

Revision ID: 8d98c76a9fe7
Revises: c15443a25a2f
Create Date: 2026-09-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d98c76a9fe7'
down_revision: Union[str, Sequence[str], None] = 'c15443a25a2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('fornecedores',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('codigo', sa.String(length=60), nullable=False),
    sa.Column('nome', sa.String(length=200), nullable=False),
    sa.Column('cnpj', sa.String(length=30), nullable=True),
    sa.Column('status', sa.Enum('ATIVO', 'INATIVO', name='status_fornecedor'), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fornecedores_codigo'), 'fornecedores', ['codigo'], unique=True)

    op.create_table('maquinas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('codigo', sa.String(length=60), nullable=False),
    sa.Column('descricao', sa.String(length=200), nullable=False),
    sa.Column('status', sa.Enum('ATIVO', 'INATIVO', name='status_maquina'), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_maquinas_codigo'), 'maquinas', ['codigo'], unique=True)

    op.create_table('departamentos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('codigo', sa.String(length=60), nullable=False),
    sa.Column('nome', sa.String(length=150), nullable=False),
    sa.Column('status', sa.Enum('ATIVO', 'INATIVO', name='status_departamento'), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_departamentos_codigo'), 'departamentos', ['codigo'], unique=True)

    op.add_column('usuarios', sa.Column('departamento_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_usuarios_departamento_id', 'usuarios', 'departamentos', ['departamento_id'], ['id'], ondelete='SET NULL'
    )

    tipo_nc = sa.Enum('FORNECEDOR', 'PROCESSO', 'CLIENTE', name='tipo_nc')
    deteccao_nc = sa.Enum('INTERNO', 'CLIENTE', 'FORNECEDOR', name='deteccao_nc')
    tipo_nc.create(op.get_bind(), checkfirst=True)
    deteccao_nc.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'nao_conformidades',
        sa.Column('tipo', tipo_nc, nullable=False, server_default='PROCESSO'),
    )
    op.add_column(
        'nao_conformidades',
        sa.Column('deteccao', deteccao_nc, nullable=True),
    )
    op.add_column('nao_conformidades', sa.Column('modo_falha', sa.String(length=200), nullable=True))
    op.add_column('nao_conformidades', sa.Column('setup', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('nao_conformidades', sa.Column('maquina_id', sa.Integer(), nullable=True))
    op.add_column('nao_conformidades', sa.Column('fornecedor_id', sa.Integer(), nullable=True))
    op.add_column('nao_conformidades', sa.Column('numero_nf_entrada', sa.String(length=50), nullable=True))
    op.add_column('nao_conformidades', sa.Column('cliente', sa.String(length=120), nullable=True))
    op.add_column('nao_conformidades', sa.Column('vendedor', sa.String(length=120), nullable=True))
    op.add_column('nao_conformidades', sa.Column('numero_nf', sa.String(length=50), nullable=True))
    op.add_column('nao_conformidades', sa.Column('data_emissao_nf', sa.Date(), nullable=True))
    op.create_foreign_key(
        'fk_nc_maquina_id', 'nao_conformidades', 'maquinas', ['maquina_id'], ['id'], ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_nc_fornecedor_id', 'nao_conformidades', 'fornecedores', ['fornecedor_id'], ['id'], ondelete='RESTRICT'
    )

    op.create_table('nc_operadores',
    sa.Column('nc_id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['nc_id'], ['nao_conformidades.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('nc_id', 'usuario_id')
    )

    op.create_table('nc_fotos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nc_id', sa.Integer(), nullable=False),
    sa.Column('nome_arquivo', sa.String(length=255), nullable=False),
    sa.Column('content_type', sa.String(length=100), nullable=False),
    sa.Column('tamanho_bytes', sa.Integer(), nullable=False),
    sa.Column('conteudo', sa.LargeBinary(), nullable=False),
    sa.Column('enviado_por_id', sa.Integer(), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['nc_id'], ['nao_conformidades.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['enviado_por_id'], ['usuarios.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('nc_fotos')
    op.drop_table('nc_operadores')

    op.drop_constraint('fk_nc_fornecedor_id', 'nao_conformidades', type_='foreignkey')
    op.drop_constraint('fk_nc_maquina_id', 'nao_conformidades', type_='foreignkey')
    op.drop_column('nao_conformidades', 'data_emissao_nf')
    op.drop_column('nao_conformidades', 'numero_nf')
    op.drop_column('nao_conformidades', 'vendedor')
    op.drop_column('nao_conformidades', 'cliente')
    op.drop_column('nao_conformidades', 'numero_nf_entrada')
    op.drop_column('nao_conformidades', 'fornecedor_id')
    op.drop_column('nao_conformidades', 'maquina_id')
    op.drop_column('nao_conformidades', 'setup')
    op.drop_column('nao_conformidades', 'modo_falha')
    op.drop_column('nao_conformidades', 'deteccao')
    op.drop_column('nao_conformidades', 'tipo')

    op.drop_constraint('fk_usuarios_departamento_id', 'usuarios', type_='foreignkey')
    op.drop_column('usuarios', 'departamento_id')

    op.drop_index(op.f('ix_departamentos_codigo'), table_name='departamentos')
    op.drop_table('departamentos')
    op.drop_index(op.f('ix_maquinas_codigo'), table_name='maquinas')
    op.drop_table('maquinas')
    op.drop_index(op.f('ix_fornecedores_codigo'), table_name='fornecedores')
    op.drop_table('fornecedores')

    sa.Enum(name='tipo_nc').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='deteccao_nc').drop(op.get_bind(), checkfirst=True)
