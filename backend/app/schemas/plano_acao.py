from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.plano_acao import (
    CategoriaIshikawa,
    MetodologiaCausaRaiz,
    ResultadoVerificacao,
    StatusPlanoAcao,
)
class CausaIshikawaCreate(BaseModel):
    categoria: CategoriaIshikawa
    descricao_causa: str = Field(min_length=1)


class CausaIshikawaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    categoria: CategoriaIshikawa
    descricao_causa: str
    marcada_como_raiz: bool


class Causa5PorquesUpsert(BaseModel):
    nivel: int = Field(ge=1, le=5)
    pergunta: str = Field(min_length=1)
    resposta: str = Field(min_length=1)


class Causa5PorquesRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nivel: int
    pergunta: str
    resposta: str
    marcada_como_raiz: bool


class MarcarRaizRequest(BaseModel):
    marcada_como_raiz: bool = True


class AcaoCorretivaCreate(BaseModel):
    descricao: str = Field(min_length=1)
    responsavel_id: int
    prazo: date


class AcaoCorretivaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ciclo: int
    descricao: str
    responsavel_id: int
    responsavel_nome: str
    prazo: date
    data_execucao: date | None
    status: str


class VerificacaoEficaciaCreate(BaseModel):
    data_verificacao: date
    responsavel_id: int
    resultado: ResultadoVerificacao
    observacoes: str | None = None


class VerificacaoEficaciaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ciclo: int
    data_verificacao: date
    responsavel_id: int
    responsavel_nome: str
    resultado: ResultadoVerificacao
    observacoes: str | None
    criado_em: datetime


class MetodologiaUpdate(BaseModel):
    metodologia_causa_raiz: MetodologiaCausaRaiz


class ConclusaoCausaRaizUpdate(BaseModel):
    conclusao_causa_raiz: str = Field(min_length=1)


class PlanoDeAcaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nc_id: int
    metodologia_causa_raiz: MetodologiaCausaRaiz
    conclusao_causa_raiz: str | None
    status: StatusPlanoAcao
    ciclo: int


class EventoHistorico(BaseModel):
    acao: str
    usuario_nome: str
    detalhe: str | None
    criado_em: datetime


class PlanoDeAcaoDetalhe(PlanoDeAcaoRead):
    numero_rnc: str = ""
    acoes_corretivas: list[AcaoCorretivaRead]
    causas_ishikawa: list[CausaIshikawaRead]
    causas_5porques: list[Causa5PorquesRead]
    verificacoes: list[VerificacaoEficaciaRead]
    historico: list[EventoHistorico] = []


class PlanoDeAcaoListItem(BaseModel):
    id: int
    nc_id: int
    numero_rnc: str
    peca_codigo: str
    peca_descricao: str
    metodologia_causa_raiz: MetodologiaCausaRaiz
    status: StatusPlanoAcao
    ciclo: int
    acoes: list[AcaoCorretivaRead]
    total_acoes: int
    acoes_concluidas: int
    acoes_atrasadas: int
    proximo_prazo: date | None


class IndicadoresPlanoAcao(BaseModel):
    total_ativos: int
    aguardando_verificacao: int
    planos_atrasados: int
    acoes_atrasadas: int
    encerrados_no_mes: int
