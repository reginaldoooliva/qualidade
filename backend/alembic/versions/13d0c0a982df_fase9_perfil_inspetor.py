"""fase9_perfil_inspetor

Revision ID: 13d0c0a982df
Revises: cff42a67dac5
Create Date: 2026-09-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '13d0c0a982df'
down_revision: Union[str, Sequence[str], None] = 'cff42a67dac5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLAlchemy's Enum(PerfilEnum, ...) grava o *nome* do membro Python (maiúsculas) como
    # valor do enum nativo do Postgres — por isso 'INSPETOR', não 'inspetor' (ver os demais
    # valores já existentes: OPERADOR, ANALISTA_QUALIDADE, GESTOR_QUALIDADE).
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE perfil_usuario ADD VALUE IF NOT EXISTS 'INSPETOR'")


def downgrade() -> None:
    """Downgrade schema."""
    # Postgres não suporta remover um valor de enum; nada a fazer no downgrade.
    pass
