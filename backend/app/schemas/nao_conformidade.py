from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.nao_conformidade import ClassificacaoNC, DisposicaoNC, OrigemNC, StatusNC
from app.schemas.caracteristica import CaracteristicaRead
from app.schemas.common import UsuarioResumo
from app.schemas.etapa import EtapaRead
from app.schemas.peca import PecaRead


class AbrirNCRequest(BaseModel):
    peca_id: int
    ordem_id: int | None = None
    etapa_id: int | None = None
    caracteristica_id: int | None = None
    rodada_id: int | None = None
    descricao_problema: str = Field(min_length=1)
    quantidade_afetada: int = Field(ge=1)
    classificacao: ClassificacaoNC
    origem: OrigemNC


class TratarNCRequest(BaseModel):
    causa_raiz_preliminar: str | None = None
    disposicao: DisposicaoNC | None = None
    responsavel_analise_id: int | None = None
    necessita_plano_acao: bool | None = None


class NaoConformidadeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_rnc: str
    peca_id: int
    ordem_id: int | None
    etapa_id: int | None
    caracteristica_id: int | None
    rodada_id: int | None
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


class NaoConformidadeDetalhe(NaoConformidadeRead):
    peca: PecaRead
    etapa: EtapaRead | None
    caracteristica: CaracteristicaRead | None
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
