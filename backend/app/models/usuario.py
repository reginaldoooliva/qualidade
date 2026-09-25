import enum

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.permissions import Perfil
from app.models.base import Base, TimestampMixin


class StatusUsuario(str, enum.Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"


class Usuario(TimestampMixin, Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    login: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[Perfil] = mapped_column(Enum(Perfil, name="perfil_usuario"), nullable=False)
    status: Mapped[StatusUsuario] = mapped_column(
        Enum(StatusUsuario, name="status_usuario"), nullable=False, default=StatusUsuario.ATIVO
    )
    departamento_id: Mapped[int | None] = mapped_column(
        ForeignKey("departamentos.id", ondelete="SET NULL"), nullable=True
    )

    departamento: Mapped["Departamento | None"] = relationship()  # noqa: F821
