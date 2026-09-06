import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class MetodologiaCausaRaiz(str, enum.Enum):
    ISHIKAWA = "ishikawa"
    CINCO_PORQUES = "cinco_porques"
    LIVRE = "livre"


class StatusPlanoAcao(str, enum.Enum):
    ABERTO = "aberto"
    EM_ANDAMENTO = "em_andamento"
    AGUARDANDO_VERIFICACAO = "aguardando_verificacao"
    ENCERRADO = "encerrado"
    REABERTO = "reaberto"


class StatusAcaoCorretiva(str, enum.Enum):
    PENDENTE = "pendente"
    CONCLUIDA = "concluida"


class CategoriaIshikawa(str, enum.Enum):
    METODO = "metodo"
    MAO_DE_OBRA = "mao_de_obra"
    MAQUINA = "maquina"
    MATERIAL = "material"
    MEIO_AMBIENTE = "meio_ambiente"
    MEDICAO = "medicao"


class ResultadoVerificacao(str, enum.Enum):
    EFICAZ = "eficaz"
    NAO_EFICAZ = "nao_eficaz"


class PlanoDeAcao(TimestampMixin, Base):
    __tablename__ = "planos_acao"

    id: Mapped[int] = mapped_column(primary_key=True)
    nc_id: Mapped[int] = mapped_column(ForeignKey("nao_conformidades.id", ondelete="CASCADE"), nullable=False)
    metodologia_causa_raiz: Mapped[MetodologiaCausaRaiz] = mapped_column(
        Enum(MetodologiaCausaRaiz, name="metodologia_causa_raiz"),
        nullable=False,
        default=MetodologiaCausaRaiz.LIVRE,
    )
    conclusao_causa_raiz: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[StatusPlanoAcao] = mapped_column(
        Enum(StatusPlanoAcao, name="status_plano_acao"), nullable=False, default=StatusPlanoAcao.ABERTO
    )
    ciclo: Mapped[int] = mapped_column(nullable=False, default=1)

    nao_conformidade: Mapped["NaoConformidade"] = relationship(back_populates="planos_acao")  # noqa: F821
    acoes_corretivas: Mapped[list["AcaoCorretiva"]] = relationship(
        back_populates="plano", cascade="all, delete-orphan", order_by="AcaoCorretiva.id"
    )
    causas_ishikawa: Mapped[list["CausaRaizIshikawa"]] = relationship(
        back_populates="plano", cascade="all, delete-orphan", order_by="CausaRaizIshikawa.id"
    )
    causas_5porques: Mapped[list["CausaRaiz5Porques"]] = relationship(
        back_populates="plano", cascade="all, delete-orphan", order_by="CausaRaiz5Porques.nivel"
    )
    verificacoes: Mapped[list["VerificacaoEficaciaPlano"]] = relationship(
        back_populates="plano", cascade="all, delete-orphan", order_by="VerificacaoEficaciaPlano.id"
    )

    @property
    def acoes_ciclo_atual(self) -> list["AcaoCorretiva"]:
        return [a for a in self.acoes_corretivas if a.ciclo == self.ciclo]


class AcaoCorretiva(Base):
    __tablename__ = "acoes_corretivas"

    id: Mapped[int] = mapped_column(primary_key=True)
    plano_id: Mapped[int] = mapped_column(ForeignKey("planos_acao.id", ondelete="CASCADE"), nullable=False)
    ciclo: Mapped[int] = mapped_column(nullable=False, default=1)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    responsavel_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    prazo: Mapped[date] = mapped_column(Date, nullable=False)
    data_execucao: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[StatusAcaoCorretiva] = mapped_column(
        Enum(StatusAcaoCorretiva, name="status_acao_corretiva"),
        nullable=False,
        default=StatusAcaoCorretiva.PENDENTE,
    )

    plano: Mapped["PlanoDeAcao"] = relationship(back_populates="acoes_corretivas")
    responsavel: Mapped["Usuario"] = relationship()  # noqa: F821

    @property
    def responsavel_nome(self) -> str:
        return self.responsavel.nome

    @property
    def status_calculado(self) -> str:
        if self.status == StatusAcaoCorretiva.PENDENTE and self.prazo < date.today():
            return "atrasada"
        return self.status.value


class CausaRaizIshikawa(Base):
    __tablename__ = "causas_ishikawa"

    id: Mapped[int] = mapped_column(primary_key=True)
    plano_id: Mapped[int] = mapped_column(ForeignKey("planos_acao.id", ondelete="CASCADE"), nullable=False)
    categoria: Mapped[CategoriaIshikawa] = mapped_column(
        Enum(CategoriaIshikawa, name="categoria_ishikawa"), nullable=False
    )
    descricao_causa: Mapped[str] = mapped_column(Text, nullable=False)
    marcada_como_raiz: Mapped[bool] = mapped_column(nullable=False, default=False)

    plano: Mapped["PlanoDeAcao"] = relationship(back_populates="causas_ishikawa")


class CausaRaiz5Porques(Base):
    __tablename__ = "causas_5porques"
    __table_args__ = (UniqueConstraint("plano_id", "nivel", name="uq_5porques_plano_nivel"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    plano_id: Mapped[int] = mapped_column(ForeignKey("planos_acao.id", ondelete="CASCADE"), nullable=False)
    nivel: Mapped[int] = mapped_column(nullable=False)
    pergunta: Mapped[str] = mapped_column(Text, nullable=False)
    resposta: Mapped[str] = mapped_column(Text, nullable=False)
    marcada_como_raiz: Mapped[bool] = mapped_column(nullable=False, default=False)

    plano: Mapped["PlanoDeAcao"] = relationship(back_populates="causas_5porques")


class VerificacaoEficaciaPlano(Base):
    __tablename__ = "verificacoes_eficacia"

    id: Mapped[int] = mapped_column(primary_key=True)
    plano_id: Mapped[int] = mapped_column(ForeignKey("planos_acao.id", ondelete="CASCADE"), nullable=False)
    ciclo: Mapped[int] = mapped_column(nullable=False, default=1)
    data_verificacao: Mapped[date] = mapped_column(Date, nullable=False)
    responsavel_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    resultado: Mapped[ResultadoVerificacao] = mapped_column(
        Enum(ResultadoVerificacao, name="resultado_verificacao"), nullable=False
    )
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    plano: Mapped["PlanoDeAcao"] = relationship(back_populates="verificacoes")
    responsavel: Mapped["Usuario"] = relationship()  # noqa: F821

    @property
    def responsavel_nome(self) -> str:
        return self.responsavel.nome
