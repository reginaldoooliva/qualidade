from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.peca import StatusCadastro


class Maquina(TimestampMixin, Base):
    __tablename__ = "maquinas"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    descricao: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[StatusCadastro] = mapped_column(
        Enum(StatusCadastro, name="status_maquina"), nullable=False, default=StatusCadastro.ATIVO
    )
