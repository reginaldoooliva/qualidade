from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.peca import StatusCadastro


class Departamento(TimestampMixin, Base):
    __tablename__ = "departamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    status: Mapped[StatusCadastro] = mapped_column(
        Enum(StatusCadastro, name="status_departamento"), nullable=False, default=StatusCadastro.ATIVO
    )
