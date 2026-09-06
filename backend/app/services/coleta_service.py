import math
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import ConflitoEstadoError, RecursoNaoEncontradoError, RegraNegocioError
from app.models.coleta import Medicao, MotivoEncerramento, RodadaColeta, StatusRodada
from app.models.peca import Caracteristica
from app.models.producao import OrdemProducao
from app.models.usuario import Usuario
from app.repositories import caracteristica_repository, coleta_repository, etapa_repository, producao_repository
from app.schemas.coleta import FinalizarColetaRequest, IniciarColetaRequest
from app.services import auditoria_service, peca_service


def _calcular_amostras(quantidade: int, numerador: int, denominador: int) -> int:
    return max(1, math.ceil(quantidade * numerador / denominador))


def iniciar(db: Session, dados: IniciarColetaRequest) -> RodadaColeta:
    peca = peca_service.obter(db, dados.peca_id)
    etapa = etapa_repository.get_by_id(db, dados.etapa_id)
    if not etapa or etapa.peca_id != peca.id:
        raise RecursoNaoEncontradoError("Etapa não encontrada para esta peça")

    ordem = producao_repository.get_by_peca_e_numero(db, peca.id, dados.numero_ordem)
    if not ordem:
        if not dados.quantidade_ordem:
            raise RegraNegocioError(
                "Esta é uma nova ordem de produção — informe a quantidade a produzir",
                code="QUANTIDADE_ORDEM_OBRIGATORIA",
            )
        ordem = producao_repository.create(
            db, OrdemProducao(peca_id=peca.id, numero_ordem=dados.numero_ordem, quantidade=dados.quantidade_ordem)
        )

    existente_em_andamento = coleta_repository.get_em_andamento(db, ordem.id, etapa.id)
    if existente_em_andamento:
        return existente_em_andamento

    existente_finalizada = coleta_repository.get_finalizada(db, ordem.id, etapa.id)
    if existente_finalizada:
        raise ConflitoEstadoError(
            "Já existe uma rodada finalizada para esta combinação de peça, ordem e etapa. "
            "Peça a um usuário de Qualidade para reabri-la.",
            code="RODADA_JA_FINALIZADA",
        )

    amostras_calculadas = _calcular_amostras(ordem.quantidade, etapa.freq_numerador, etapa.freq_denominador)
    rodada = RodadaColeta(
        ordem_id=ordem.id,
        etapa_id=etapa.id,
        amostras_calculadas=amostras_calculadas,
        amostras_ajustadas=dados.amostras_ajustadas,
        justificativa_ajuste=dados.justificativa_ajuste,
    )
    return coleta_repository.create(db, rodada)


def obter(db: Session, rodada_id: int) -> RodadaColeta:
    rodada = coleta_repository.get_by_id(db, rodada_id)
    if not rodada:
        raise RecursoNaoEncontradoError(f"Rodada {rodada_id} não encontrada")
    return rodada


def salvar_medicao(
    db: Session, rodada_id: int, caracteristica_id: int, amostra_numero: int, valor: float, operador: Usuario
) -> Medicao:
    rodada = obter(db, rodada_id)
    if rodada.status != StatusRodada.EM_ANDAMENTO:
        raise ConflitoEstadoError(
            "Esta rodada já foi finalizada — reabra-a para editar medições", code="RODADA_NAO_EM_ANDAMENTO"
        )
    if amostra_numero < 1 or amostra_numero > rodada.amostras_alvo:
        raise RegraNegocioError(
            f"Número de amostra deve estar entre 1 e {rodada.amostras_alvo}", code="AMOSTRA_FORA_DO_INTERVALO"
        )

    caracteristica = caracteristica_repository.get_by_id(db, caracteristica_id)
    if not caracteristica or caracteristica.etapa_id != rodada.etapa_id:
        raise RecursoNaoEncontradoError("Característica não pertence à etapa desta rodada")

    medicao = coleta_repository.get_medicao(db, rodada_id, caracteristica_id, amostra_numero)
    if medicao:
        medicao.valor = valor
        medicao.operador_id = operador.id
        medicao.data_hora = datetime.now(timezone.utc)
        db.commit()
        db.refresh(medicao)
    else:
        medicao = Medicao(
            rodada_id=rodada_id,
            caracteristica_id=caracteristica_id,
            amostra_numero=amostra_numero,
            valor=valor,
            operador_id=operador.id,
        )
        db.add(medicao)
        db.commit()
        db.refresh(medicao)
    return medicao


def excluir_medicao(db: Session, rodada_id: int, caracteristica_id: int, amostra_numero: int) -> None:
    rodada = obter(db, rodada_id)
    if rodada.status != StatusRodada.EM_ANDAMENTO:
        raise ConflitoEstadoError("Esta rodada já foi finalizada", code="RODADA_NAO_EM_ANDAMENTO")
    medicao = coleta_repository.get_medicao(db, rodada_id, caracteristica_id, amostra_numero)
    if medicao:
        coleta_repository.delete_medicao(db, medicao)


def _amostras_completas(rodada: RodadaColeta, caracteristicas: list[Caracteristica]) -> int:
    total_caracteristicas = len(caracteristicas)
    if total_caracteristicas == 0:
        return 0
    contagem: dict[int, int] = {}
    for medicao in rodada.medicoes:
        contagem[medicao.amostra_numero] = contagem.get(medicao.amostra_numero, 0) + 1
    return sum(1 for qtd in contagem.values() if qtd >= total_caracteristicas)


def _fora_de_especificacao(medicao: Medicao, caracteristicas: list[Caracteristica]) -> bool:
    caracteristica = next((c for c in caracteristicas if c.id == medicao.caracteristica_id), None)
    if not caracteristica:
        return False
    valor = float(medicao.valor)
    return valor < caracteristica.lie or valor > caracteristica.lse


def finalizar(db: Session, rodada_id: int, dados: FinalizarColetaRequest) -> tuple[RodadaColeta, bool]:
    rodada = obter(db, rodada_id)
    if rodada.status != StatusRodada.EM_ANDAMENTO:
        raise ConflitoEstadoError("Esta rodada já está finalizada", code="RODADA_NAO_EM_ANDAMENTO")

    caracteristicas = caracteristica_repository.list_by_etapa(db, rodada.etapa_id)
    amostras_completas = _amostras_completas(rodada, caracteristicas)
    algum_fora_especificacao = any(_fora_de_especificacao(m, caracteristicas) for m in rodada.medicoes)

    if amostras_completas < rodada.amostras_alvo:
        if not dados.motivo_encerramento_antecipado:
            raise RegraNegocioError(
                f"Faltam {rodada.amostras_alvo - amostras_completas} amostra(s) — informe o motivo do "
                "encerramento antecipado para finalizar mesmo assim",
                code="MOTIVO_ENCERRAMENTO_OBRIGATORIO",
            )
        if dados.motivo_encerramento_antecipado == MotivoEncerramento.OUTRO and not dados.motivo_detalhe:
            raise RegraNegocioError("Descreva o motivo em 'Outro'", code="MOTIVO_DETALHE_OBRIGATORIO")
        rodada.status = StatusRodada.FINALIZADA_COM_PENDENCIA
        rodada.motivo_encerramento_antecipado = dados.motivo_encerramento_antecipado
        rodada.motivo_detalhe = dados.motivo_detalhe
    else:
        rodada.status = StatusRodada.FINALIZADA

    coleta_repository.update(db, rodada)

    sugestao_abrir_rnc = (
        algum_fora_especificacao or dados.motivo_encerramento_antecipado == MotivoEncerramento.NAO_CONFORMIDADE_PROCESSO
    )
    return rodada, sugestao_abrir_rnc


def reabrir(db: Session, rodada_id: int, usuario: Usuario) -> RodadaColeta:
    rodada = obter(db, rodada_id)
    if rodada.status == StatusRodada.EM_ANDAMENTO:
        raise ConflitoEstadoError("Rodada já está em andamento", code="RODADA_JA_EM_ANDAMENTO")

    status_anterior = rodada.status
    rodada.status = StatusRodada.EM_ANDAMENTO
    rodada.motivo_encerramento_antecipado = None
    rodada.motivo_detalhe = None
    coleta_repository.update(db, rodada)

    auditoria_service.registrar(
        db,
        entidade="rodada_coleta",
        entidade_id=rodada.id,
        acao="reabertura",
        usuario=usuario,
        detalhe=f"status anterior: {status_anterior.value}",
    )
    return rodada
