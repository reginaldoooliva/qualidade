from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.nao_conformidade import (
    ClassificacaoNC,
    DeteccaoNC,
    DisposicaoNC,
    OrigemNC,
    StatusAcaoDepartamental,
    StatusNC,
    TipoNC,
)
from app.schemas.caracteristica import CaracteristicaRead
from app.schemas.common import UsuarioResumo
from app.schemas.departamento import DepartamentoRead
from app.schemas.etapa import EtapaRead
from app.schemas.fornecedor import FornecedorRead
from app.schemas.maquina import MaquinaRead
from app.schemas.peca import PecaRead


class AbrirNCRequest(BaseModel):
    tipo: TipoNC = TipoNC.PROCESSO
    peca_id: int
    ordem_id: int | None = None
    etapa_id: int | None = None
    caracteristica_id: int | None = None
    rodada_id: int | None = None
    descricao_problema: str = Field(min_length=1)
    quantidade_afetada: int = Field(ge=1)
    classificacao: ClassificacaoNC
    origem: OrigemNC
    deteccao: DeteccaoNC | None = None
    modo_falha: str | None = None

    # Tipo = processo
    maquina_id: int | None = None
    operadores_ids: list[int] = []
    setup: bool = False

    # Tipo = fornecedor
    fornecedor_id: int | None = None
    numero_nf_entrada: str | None = None

    # Tipo = cliente
    cliente: str | None = None
    vendedor: str | None = None
    numero_nf: str | None = None
    data_emissao_nf: date | None = None

    @model_validator(mode="after")
    def _validar_campos_por_tipo(self) -> "AbrirNCRequest":
        if self.tipo == TipoNC.FORNECEDOR and self.fornecedor_id is None:
            raise ValueError("fornecedor_id é obrigatório quando tipo é 'fornecedor'")
        if self.tipo == TipoNC.CLIENTE and not self.cliente:
            raise ValueError("cliente é obrigatório quando tipo é 'cliente'")
        return self


class TratarNCRequest(BaseModel):
    causa_raiz_preliminar: str | None = None
    disposicao: DisposicaoNC | None = None
    responsavel_analise_id: int | None = None
    necessita_plano_acao: bool | None = None


class NaoConformidadeFotoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome_arquivo: str
    content_type: str
    tamanho_bytes: int
    criado_em: datetime


class NaoConformidadeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_rnc: str
    tipo: TipoNC
    deteccao: DeteccaoNC | None
    modo_falha: str | None
    setup: bool
    peca_id: int
    ordem_id: int | None
    etapa_id: int | None
    caracteristica_id: int | None
    rodada_id: int | None
    maquina_id: int | None
    fornecedor_id: int | None
    numero_nf_entrada: str | None
    cliente: str | None
    vendedor: str | None
    numero_nf: str | None
    data_emissao_nf: date | None
    descricao_problema: str
    quantidade_afetada: int
    classificacao: ClassificacaoNC
    origem: OrigemNC
    causa_raiz_preliminar: str | None
    disposicao: DisposicaoNC | None
    responsavel_analise_id: int | None
    necessita_plano_acao: bool
    aberto_por_id: int
    aberto_por_nome: str
    data_abertura: datetime
    data_encerramento: datetime | None
    status: StatusNC


class NaoConformidadeListItem(NaoConformidadeRead):
    peca_codigo: str = ""
    peca_descricao: str = ""
    plano_acao_id: int | None = None
    plano_acao_status: str | None = None
    tem_plano_aberto: bool = False


class EventoHistorico(BaseModel):
    acao: str
    usuario_nome: str
    detalhe: str | None
    criado_em: datetime


class PlanoAcaoResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    ciclo: int


class AcaoDepartamentalCreate(BaseModel):
    departamento_id: int
    descricao: str = Field(min_length=1)


class AcaoDepartamentalConcluirRequest(BaseModel):
    observacao: str = Field(min_length=1)


class AcaoDepartamentalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nc_id: int
    departamento_id: int
    departamento: DepartamentoRead
    descricao: str
    status: StatusAcaoDepartamental
    observacao_conclusao: str | None
    criado_por_id: int
    criado_por_nome: str
    concluido_por_id: int | None
    concluido_por_nome: str | None
    concluido_em: datetime | None
    criado_em: datetime


class AcaoDepartamentalListItem(AcaoDepartamentalRead):
    numero_rnc: str = ""
    peca_codigo: str = ""
    peca_descricao: str = ""


class NaoConformidadeDetalhe(NaoConformidadeRead):
    peca: PecaRead
    etapa: EtapaRead | None
    caracteristica: CaracteristicaRead | None
    maquina: MaquinaRead | None
    fornecedor: FornecedorRead | None
    operadores: list[UsuarioResumo] = []
    fotos: list[NaoConformidadeFotoRead] = []
    acoes_departamentais: list[AcaoDepartamentalRead] = []
    tem_acao_departamental_pendente: bool = False
    responsavel_analise: UsuarioResumo | None
    plano_acao_ativo_id: int | None = None
    tem_plano_aberto: bool = False
    planos_acao: list[PlanoAcaoResumo] = []
    historico: list[EventoHistorico] = []


class IndicadoresNC(BaseModel):
    abertas: int
    em_analise: int
    em_tratamento: int
    encerradas_no_mes: int
    com_plano_aberto: int
    acoes_atrasadas: int
