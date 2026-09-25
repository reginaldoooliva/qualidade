from app.models.auditoria import LogAuditoria
from app.models.base import Base
from app.models.bloqueio_deposito import BloqueioDeposito, StatusBloqueioDeposito
from app.models.coleta import Medicao, MotivoEncerramento, RodadaColeta, StatusRodada
from app.models.departamento import Departamento
from app.models.fornecedor import Fornecedor
from app.models.maquina import Maquina
from app.models.nao_conformidade import (
    AcaoDepartamental,
    ClassificacaoNC,
    DeteccaoNC,
    DisposicaoNC,
    NaoConformidade,
    NaoConformidadeFoto,
    OrigemNC,
    StatusAcaoDepartamental,
    StatusNC,
    TipoNC,
)
from app.models.peca import Caracteristica, Etapa, Peca
from app.models.plano_acao import (
    AcaoCorretiva,
    CategoriaIshikawa,
    CausaRaiz5Porques,
    CausaRaizIshikawa,
    MetodologiaCausaRaiz,
    PlanoDeAcao,
    ResultadoVerificacao,
    StatusAcaoCorretiva,
    StatusPlanoAcao,
    VerificacaoEficaciaPlano,
)
from app.models.producao import OrdemProducao
from app.models.tipo_instrumento import TipoInstrumento
from app.models.usuario import Usuario

__all__ = [
    "Base",
    "Usuario",
    "Peca",
    "Etapa",
    "Caracteristica",
    "Fornecedor",
    "Maquina",
    "Departamento",
    "TipoInstrumento",
    "OrdemProducao",
    "RodadaColeta",
    "Medicao",
    "StatusRodada",
    "MotivoEncerramento",
    "LogAuditoria",
    "BloqueioDeposito",
    "StatusBloqueioDeposito",
    "NaoConformidade",
    "NaoConformidadeFoto",
    "AcaoDepartamental",
    "StatusAcaoDepartamental",
    "StatusNC",
    "TipoNC",
    "DeteccaoNC",
    "ClassificacaoNC",
    "OrigemNC",
    "DisposicaoNC",
    "PlanoDeAcao",
    "AcaoCorretiva",
    "CausaRaizIshikawa",
    "CausaRaiz5Porques",
    "VerificacaoEficaciaPlano",
    "MetodologiaCausaRaiz",
    "StatusPlanoAcao",
    "StatusAcaoCorretiva",
    "CategoriaIshikawa",
    "ResultadoVerificacao",
]
