from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.peca import StatusCadastro


class Fornecedor(TimestampMixin, Base):
    __tablename__ = "fornecedores"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[StatusCadastro] = mapped_column(
        Enum(StatusCadastro, name="status_fornecedor"), nullable=False, default=StatusCadastro.ATIVO
    )
