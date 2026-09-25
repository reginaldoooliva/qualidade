import enum
from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, LargeBinary, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.plano_acao import StatusPlanoAcao


class StatusNC(str, enum.Enum):
    ABERTA = "aberta"
    EM_ANALISE = "em_analise"
    EM_TRATAMENTO = "em_tratamento"
    ENCERRADA = "encerrada"


class ClassificacaoNC(str, enum.Enum):
    CRITICA = "critica"
    MAIOR = "maior"
    MENOR = "menor"


class OrigemNC(str, enum.Enum):
    PROCESSO = "processo"
    MATERIA_PRIMA = "materia_prima"
    PROJETO = "projeto"
    INSTRUMENTO = "instrumento"
    MAO_DE_OBRA = "mao_de_obra"
    OUTRO = "outro"


class DisposicaoNC(str, enum.Enum):
    RETRABALHO = "retrabalho"
    SUCATA = "sucata"
    USO_COMO_ESTA = "uso_como_esta"
    DEVOLUCAO_FORNECEDOR = "devolucao_fornecedor"
    RECLASSIFICACAO = "reclassificacao"


class TipoNC(str, enum.Enum):
    FORNECEDOR = "fornecedor"
    PROCESSO = "processo"
    CLIENTE = "cliente"


class DeteccaoNC(str, enum.Enum):
    INTERNO = "interno"
    CLIENTE = "cliente"
    FORNECEDOR = "fornecedor"


class StatusAcaoDepartamental(str, enum.Enum):
    PENDENTE = "pendente"
    CONCLUIDA = "concluida"


nc_operadores = Table(
    "nc_operadores",
    Base.metadata,
    Column("nc_id", ForeignKey("nao_conformidades.id", ondelete="CASCADE"), primary_key=True),
    Column("usuario_id", ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
)


class NaoConformidade(TimestampMixin, Base):
    __tablename__ = "nao_conformidades"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero_rnc: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)

    tipo: Mapped[TipoNC] = mapped_column(Enum(TipoNC, name="tipo_nc"), nullable=False, default=TipoNC.PROCESSO)
    deteccao: Mapped[DeteccaoNC | None] = mapped_column(Enum(DeteccaoNC, name="deteccao_nc"), nullable=True)
    modo_falha: Mapped[str | None] = mapped_column(String(200), nullable=True)
    setup: Mapped[bool] = mapped_column(nullable=False, default=False)

    peca_id: Mapped[int] = mapped_column(ForeignKey("pecas.id", ondelete="RESTRICT"), nullable=False)
    ordem_id: Mapped[int | None] = mapped_column(ForeignKey("ordens_producao.id", ondelete="SET NULL"), nullable=True)
    etapa_id: Mapped[int | None] = mapped_column(ForeignKey("etapas.id", ondelete="SET NULL"), nullable=True)
    caracteristica_id: Mapped[int | None] = mapped_column(
        ForeignKey("caracteristicas.id", ondelete="SET NULL"), nullable=True
    )
    rodada_id: Mapped[int | None] = mapped_column(
        ForeignKey("rodadas_coleta.id", ondelete="SET NULL"), nullable=True
    )
    maquina_id: Mapped[int | None] = mapped_column(ForeignKey("maquinas.id", ondelete="SET NULL"), nullable=True)

    # Tipo = fornecedor
    fornecedor_id: Mapped[int | None] = mapped_column(ForeignKey("fornecedores.id", ondelete="RESTRICT"), nullable=True)
    numero_nf_entrada: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Tipo = cliente
    cliente: Mapped[str | None] = mapped_column(String(120), nullable=True)
    vendedor: Mapped[str | None] = mapped_column(String(120), nullable=True)
    numero_nf: Mapped[str | None] = mapped_column(String(50), nullable=True)
    data_emissao_nf: Mapped[date | None] = mapped_column(Date, nullable=True)

    descricao_problema: Mapped[str] = mapped_column(Text, nullable=False)
    quantidade_afetada: Mapped[int] = mapped_column(nullable=False)
    classificacao: Mapped[ClassificacaoNC] = mapped_column(Enum(ClassificacaoNC, name="classificacao_nc"), nullable=False)
    origem: Mapped[OrigemNC] = mapped_column(Enum(OrigemNC, name="origem_nc"), nullable=False)

    causa_raiz_preliminar: Mapped[str | None] = mapped_column(Text, nullable=True)
    disposicao: Mapped[DisposicaoNC | None] = mapped_column(Enum(DisposicaoNC, name="disposicao_nc"), nullable=True)
    responsavel_analise_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=True
    )
    necessita_plano_acao: Mapped[bool] = mapped_column(nullable=False, default=False)

    aberto_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    data_abertura: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    data_encerramento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[StatusNC] = mapped_column(Enum(StatusNC, name="status_nc"), nullable=False, default=StatusNC.ABERTA)

    peca: Mapped["Peca"] = relationship()  # noqa: F821
    ordem: Mapped["OrdemProducao | None"] = relationship()  # noqa: F821
    etapa: Mapped["Etapa | None"] = relationship()  # noqa: F821
    caracteristica: Mapped["Caracteristica | None"] = relationship()  # noqa: F821
    rodada: Mapped["RodadaColeta | None"] = relationship()  # noqa: F821
    maquina: Mapped["Maquina | None"] = relationship()  # noqa: F821
    fornecedor: Mapped["Fornecedor | None"] = relationship()  # noqa: F821
    operadores: Mapped[list["Usuario"]] = relationship(secondary=nc_operadores)  # noqa: F821
    fotos: Mapped[list["NaoConformidadeFoto"]] = relationship(
        back_populates="nao_conformidade", cascade="all, delete-orphan", order_by="NaoConformidadeFoto.id"
    )
    acoes_departamentais: Mapped[list["AcaoDepartamental"]] = relationship(
        back_populates="nao_conformidade", cascade="all, delete-orphan", order_by="AcaoDepartamental.id"
    )
    aberto_por: Mapped["Usuario"] = relationship(foreign_keys=[aberto_por_id])  # noqa: F821
    responsavel_analise: Mapped["Usuario | None"] = relationship(foreign_keys=[responsavel_analise_id])  # noqa: F821
    planos_acao: Mapped[list["PlanoDeAcao"]] = relationship(  # noqa: F821
        back_populates="nao_conformidade", order_by="PlanoDeAcao.id"
    )

    @property
    def aberto_por_nome(self) -> str:
        return self.aberto_por.nome

    @property
    def plano_acao_ativo(self) -> "PlanoDeAcao | None":  # noqa: F821
        for plano in self.planos_acao:
            if plano.status != StatusPlanoAcao.ENCERRADO:
                return plano
        return None

    @property
    def tem_plano_aberto(self) -> bool:
        return self.status == StatusNC.ENCERRADA and self.plano_acao_ativo is not None

    @property
    def tem_acao_departamental_pendente(self) -> bool:
        return any(a.status == StatusAcaoDepartamental.PENDENTE for a in self.acoes_departamentais)


class NaoConformidadeFoto(TimestampMixin, Base):
    __tablename__ = "nc_fotos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nc_id: Mapped[int] = mapped_column(ForeignKey("nao_conformidades.id", ondelete="CASCADE"), nullable=False)
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(nullable=False)
    conteudo: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    enviado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)

    nao_conformidade: Mapped["NaoConformidade"] = relationship(back_populates="fotos")


class AcaoDepartamental(TimestampMixin, Base):
    __tablename__ = "nc_acoes_departamentais"

    id: Mapped[int] = mapped_column(primary_key=True)
    nc_id: Mapped[int] = mapped_column(ForeignKey("nao_conformidades.id", ondelete="CASCADE"), nullable=False)
    departamento_id: Mapped[int] = mapped_column(ForeignKey("departamentos.id", ondelete="RESTRICT"), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[StatusAcaoDepartamental] = mapped_column(
        Enum(StatusAcaoDepartamental, name="status_acao_departamental"),
        nullable=False,
        default=StatusAcaoDepartamental.PENDENTE,
    )
    observacao_conclusao: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    concluido_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=True)
    concluido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    nao_conformidade: Mapped["NaoConformidade"] = relationship(back_populates="acoes_departamentais")
    departamento: Mapped["Departamento"] = relationship()  # noqa: F821
    criado_por: Mapped["Usuario"] = relationship(foreign_keys=[criado_por_id])  # noqa: F821
    concluido_por: Mapped["Usuario | None"] = relationship(foreign_keys=[concluido_por_id])  # noqa: F821

    @property
    def criado_por_nome(self) -> str:
        return self.criado_por.nome

    @property
    def concluido_por_nome(self) -> str | None:
        return self.concluido_por.nome if self.concluido_por else None
