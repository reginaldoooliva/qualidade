import enum

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class StatusCadastro(str, enum.Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"


class UnidadeMedida(str, enum.Enum):
    MM = "mm"
    CM = "cm"
    POLEGADA = "polegada"


class InstrumentoMedicao(str, enum.Enum):
    PAQUIMETRO = "paquimetro"
    MICROMETRO = "micrometro"
    RELOGIO_COMPARADOR = "relogio_comparador"
    OUTRO = "outro"


class Peca(TimestampMixin, Base):
    __tablename__ = "pecas"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    descricao: Mapped[str] = mapped_column(String(200), nullable=False)
    cliente: Mapped[str | None] = mapped_column(String(120), nullable=True)
    desenho: Mapped[str | None] = mapped_column(String(120), nullable=True)
    revisao: Mapped[str] = mapped_column(String(30), nullable=False)
    material: Mapped[str | None] = mapped_column(String(120), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[StatusCadastro] = mapped_column(
        Enum(StatusCadastro, name="status_peca"), nullable=False, default=StatusCadastro.ATIVO
    )

    etapas: Mapped[list["Etapa"]] = relationship(
        back_populates="peca", cascade="all, delete-orphan", order_by="Etapa.numero_etapa"
    )


class Etapa(TimestampMixin, Base):
    __tablename__ = "etapas"
    __table_args__ = (UniqueConstraint("peca_id", "numero_etapa", name="uq_etapa_peca_numero"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    peca_id: Mapped[int] = mapped_column(ForeignKey("pecas.id", ondelete="CASCADE"), nullable=False)
    numero_etapa: Mapped[int] = mapped_column(nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(200), nullable=True)
    freq_numerador: Mapped[int] = mapped_column(nullable=False, default=1)
    freq_denominador: Mapped[int] = mapped_column(nullable=False, default=1)
    status: Mapped[StatusCadastro] = mapped_column(
        Enum(StatusCadastro, name="status_etapa"), nullable=False, default=StatusCadastro.ATIVO
    )

    peca: Mapped["Peca"] = relationship(back_populates="etapas")
    caracteristicas: Mapped[list["Caracteristica"]] = relationship(
        back_populates="etapa", cascade="all, delete-orphan"
    )


class Caracteristica(TimestampMixin, Base):
    __tablename__ = "caracteristicas"

    id: Mapped[int] = mapped_column(primary_key=True)
    etapa_id: Mapped[int] = mapped_column(ForeignKey("etapas.id", ondelete="CASCADE"), nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    posicao_desenho: Mapped[str | None] = mapped_column(String(30), nullable=True)
    nominal: Mapped[float] = mapped_column(Numeric(12, 5), nullable=False)
    tol_superior: Mapped[float] = mapped_column(Numeric(12, 5), nullable=False, default=0)
    tol_inferior: Mapped[float] = mapped_column(Numeric(12, 5), nullable=False, default=0)
    unidade: Mapped[UnidadeMedida] = mapped_column(
        Enum(UnidadeMedida, name="unidade_medida"), nullable=False, default=UnidadeMedida.MM
    )
    instrumento: Mapped[InstrumentoMedicao | None] = mapped_column(
        Enum(InstrumentoMedicao, name="instrumento_medicao"), nullable=True
    )
    casas_decimais: Mapped[int] = mapped_column(nullable=False, default=3)
    status: Mapped[StatusCadastro] = mapped_column(
        Enum(StatusCadastro, name="status_caracteristica"), nullable=False, default=StatusCadastro.ATIVO
    )

    etapa: Mapped["Etapa"] = relationship(back_populates="caracteristicas")

    @property
    def lse(self) -> float:
        return float(self.nominal) + float(self.tol_superior)

    @property
    def lie(self) -> float:
        return float(self.nominal) - float(self.tol_inferior)
