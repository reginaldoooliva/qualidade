"""fase10_tipos_instrumento

Revision ID: aba4f15bb309
Revises: cf2c74038cd1
Create Date: 2026-09-24 19:06:01.254543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aba4f15bb309'
down_revision: Union[str, Sequence[str], None] = 'cf2c74038cd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Rótulos dos 4 valores do enum antigo, na ordem em que viram registros no novo cadastro.
TIPOS_INICIAIS = [
    ('PAQUIMETRO', 'Paquímetro'),
    ('MICROMETRO', 'Micrômetro'),
    ('RELOGIO_COMPARADOR', 'Relógio comparador'),
    ('OUTRO', 'Outro'),
]


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('tipos_instrumento',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(length=150), nullable=False),
    sa.Column('descricao_funcao', sa.Text(), nullable=True),
    sa.Column('imagem_conteudo', sa.LargeBinary(), nullable=True),
    sa.Column('imagem_nome_arquivo', sa.String(length=255), nullable=True),
    sa.Column('imagem_content_type', sa.String(length=100), nullable=True),
    sa.Column('status', sa.Enum('ATIVO', 'INATIVO', name='status_tipo_instrumento'), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tipos_instrumento_nome'), 'tipos_instrumento', ['nome'], unique=True)

    tipos_instrumento = sa.table(
        'tipos_instrumento',
        sa.column('nome', sa.String),
        sa.column('status', sa.String),
    )
    op.bulk_insert(tipos_instrumento, [{'nome': nome, 'status': 'ATIVO'} for _, nome in TIPOS_INICIAIS])

    op.add_column(
        'caracteristicas',
        sa.Column('tipo_instrumento_id', sa.Integer(), sa.ForeignKey('tipos_instrumento.id', ondelete='RESTRICT'), nullable=True),
    )

    bind = op.get_bind()
    for enum_valor, nome in TIPOS_INICIAIS:
        bind.execute(
            sa.text(
                "UPDATE caracteristicas SET tipo_instrumento_id = "
                "(SELECT id FROM tipos_instrumento WHERE nome = :nome) "
                "WHERE instrumento = :enum_valor"
            ),
            {'nome': nome, 'enum_valor': enum_valor},
        )

    op.drop_column('caracteristicas', 'instrumento')
    sa.Enum(name='instrumento_medicao').drop(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    """Downgrade schema."""
    instrumento_medicao = sa.Enum('PAQUIMETRO', 'MICROMETRO', 'RELOGIO_COMPARADOR', 'OUTRO', name='instrumento_medicao')
    instrumento_medicao.create(op.get_bind(), checkfirst=True)
    op.add_column('caracteristicas', sa.Column('instrumento', instrumento_medicao, nullable=True))

    bind = op.get_bind()
    for enum_valor, nome in TIPOS_INICIAIS:
        bind.execute(
            sa.text(
                "UPDATE caracteristicas SET instrumento = :enum_valor "
                "WHERE tipo_instrumento_id = (SELECT id FROM tipos_instrumento WHERE nome = :nome)"
            ),
            {'nome': nome, 'enum_valor': enum_valor},
        )

    op.drop_column('caracteristicas', 'tipo_instrumento_id')
    op.drop_index(op.f('ix_tipos_instrumento_nome'), table_name='tipos_instrumento')
    op.drop_table('tipos_instrumento')
    sa.Enum(name='status_tipo_instrumento').drop(op.get_bind(), checkfirst=True)
