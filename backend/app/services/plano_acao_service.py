from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNaoEncontradoError, RegraNegocioError
from app.models.plano_acao import (
    AcaoCorretiva,
    CausaRaiz5Porques,
    CausaRaizIshikawa,
    MetodologiaCausaRaiz,
    PlanoDeAcao,
    ResultadoVerificacao,
    StatusAcaoCorretiva,
    StatusPlanoAcao,
    VerificacaoEficaciaPlano,
)
from app.models.usuario import Usuario
from app.repositories import plano_acao_repository, usuario_repository
from app.schemas.plano_acao import (
    AcaoCorretivaCreate,
    AcaoCorretivaRead,
    Causa5PorquesUpsert,
    CausaIshikawaCreate,
    EventoHistorico,
    PlanoDeAcaoDetalhe,
    PlanoDeAcaoListItem,
    VerificacaoEficaciaCreate,
)
from app.services import auditoria_service
from app.services.auditoria_service import listar_por_entidade


def obter(db: Session, plano_id: int) -> PlanoDeAcao:
    plano = plano_acao_repository.get_by_id(db, plano_id)
    if not plano:
        raise RecursoNaoEncontradoError(f"Plano de Ação {plano_id} não encontrado")
    return plano


def _checar_usuario(db: Session, usuario_id: int) -> Usuario:
    usuario = usuario_repository.get_by_id(db, usuario_id)
    if not usuario:
        raise RecursoNaoEncontradoError(f"Usuário {usuario_id} não encontrado")
    return usuario


def trocar_metodologia(
    db: Session, plano_id: int, metodologia: MetodologiaCausaRaiz, usuario: Usuario
) -> PlanoDeAcao:
    plano = obter(db, plano_id)
    if plano.metodologia_causa_raiz == metodologia:
        return plano
    anterior = plano.metodologia_causa_raiz
    plano.metodologia_causa_raiz = metodologia
    plano.conclusao_causa_raiz = None
    plano_acao_repository.update(db, plano)
    auditoria_service.registrar(
        db,
        entidade="plano_acao",
        entidade_id=plano.id,
        acao="troca_metodologia",
        usuario=usuario,
        detalhe=f"{anterior.value} -> {metodologia.value} (dados anteriores preservados no histórico)",
    )
    return plano


def atualizar_conclusao(db: Session, plano_id: int, conclusao: str, usuario: Usuario) -> PlanoDeAcao:
    plano = obter(db, plano_id)
    plano.conclusao_causa_raiz = conclusao
    return plano_acao_repository.update(db, plano)


def _recalcular_conclusao(plano: PlanoDeAcao) -> None:
    if plano.metodologia_causa_raiz == MetodologiaCausaRaiz.ISHIKAWA:
        marcadas = [c.descricao_causa for c in plano.causas_ishikawa if c.marcada_como_raiz]
        plano.conclusao_causa_raiz = "; ".join(marcadas) or None
    elif plano.metodologia_causa_raiz == MetodologiaCausaRaiz.CINCO_PORQUES:
        marcadas = [c.resposta for c in plano.causas_5porques if c.marcada_como_raiz]
        plano.conclusao_causa_raiz = "; ".join(marcadas) or None


def adicionar_causa_ishikawa(
    db: Session, plano_id: int, dados: CausaIshikawaCreate, usuario: Usuario
) -> CausaRaizIshikawa:
    plano = obter(db, plano_id)
    causa = CausaRaizIshikawa(plano_id=plano.id, categoria=dados.categoria, descricao_causa=dados.descricao_causa)
    return plano_acao_repository.add_causa_ishikawa(db, causa)


def marcar_causa_ishikawa(db: Session, plano_id: int, causa_id: int, marcada: bool, usuario: Usuario) -> PlanoDeAcao:
    plano = obter(db, plano_id)
    causa = plano_acao_repository.get_causa_ishikawa(db, plano_id, causa_id)
    if not causa:
        raise RecursoNaoEncontradoError("Causa não encontrada neste plano")
    causa.marcada_como_raiz = marcada
    plano_acao_repository.update_causa_ishikawa(db, causa)
    _recalcular_conclusao(plano)
    return plano_acao_repository.update(db, plano)


def remover_causa_ishikawa(db: Session, plano_id: int, causa_id: int, usuario: Usuario) -> None:
    causa = plano_acao_repository.get_causa_ishikawa(db, plano_id, causa_id)
    if not causa:
        raise RecursoNaoEncontradoError("Causa não encontrada neste plano")
    plano_acao_repository.delete_causa_ishikawa(db, causa)


def upsert_causa_5porques(
    db: Session, plano_id: int, dados: Causa5PorquesUpsert, usuario: Usuario
) -> CausaRaiz5Porques:
    plano = obter(db, plano_id)
    existente = plano_acao_repository.get_causa_5porques_por_nivel(db, plano_id, dados.nivel)
    if existente:
        existente.pergunta = dados.pergunta
        existente.resposta = dados.resposta
        return plano_acao_repository.upsert_causa_5porques(db, existente)
    causa = CausaRaiz5Porques(plano_id=plano.id, nivel=dados.nivel, pergunta=dados.pergunta, resposta=dados.resposta)
    return plano_acao_repository.upsert_causa_5porques(db, causa)


def marcar_causa_5porques(db: Session, plano_id: int, causa_id: int, marcada: bool, usuario: Usuario) -> PlanoDeAcao:
    plano = obter(db, plano_id)
    causa = plano_acao_repository.get_causa_5porques(db, plano_id, causa_id)
    if not causa:
        raise RecursoNaoEncontradoError("Causa não encontrada neste plano")
    causa.marcada_como_raiz = marcada
    plano_acao_repository.upsert_causa_5porques(db, causa)
    _recalcular_conclusao(plano)
    return plano_acao_repository.update(db, plano)


def adicionar_acao(db: Session, plano_id: int, dados: AcaoCorretivaCreate, usuario: Usuario) -> PlanoDeAcao:
    plano = obter(db, plano_id)
    if plano.status == StatusPlanoAcao.ENCERRADO:
        raise RegraNegocioError("Este plano de ação já está encerrado", code="PLANO_ENCERRADO")
    _checar_usuario(db, dados.responsavel_id)

    acao = AcaoCorretiva(
        plano_id=plano.id,
        ciclo=plano.ciclo,
        descricao=dados.descricao,
        responsavel_id=dados.responsavel_id,
        prazo=dados.prazo,
    )
    plano_acao_repository.add_acao(db, acao)

    if plano.status in (StatusPlanoAcao.ABERTO, StatusPlanoAcao.REABERTO):
        status_anterior = plano.status
        plano.status = StatusPlanoAcao.EM_ANDAMENTO
        plano_acao_repository.update(db, plano)
        auditoria_service.registrar(
            db,
            entidade="plano_acao",
            entidade_id=plano.id,
            acao="mudanca_status",
            usuario=usuario,
            detalhe=f"{status_anterior.value} -> {plano.status.value}",
        )
    return obter(db, plano.id)


def concluir_acao(db: Session, plano_id: int, acao_id: int, usuario: Usuario) -> PlanoDeAcao:
    plano = obter(db, plano_id)
    acao = plano_acao_repository.get_acao(db, plano_id, acao_id)
    if not acao:
        raise RecursoNaoEncontradoError("Ação corretiva não encontrada neste plano")
    acao.status = StatusAcaoCorretiva.CONCLUIDA
    acao.data_execucao = date.today()
    plano_acao_repository.update_acao(db, acao)
    return obter(db, plano.id)


def avancar_verificacao(db: Session, plano_id: int, usuario: Usuario) -> PlanoDeAcao:
    plano = obter(db, plano_id)
    if plano.status != StatusPlanoAcao.EM_ANDAMENTO:
        raise RegraNegocioError(
            "Só é possível avançar para verificação de eficácia a partir de 'Em andamento'",
            code="PLANO_STATUS_INVALIDO",
        )
    acoes_atuais = plano.acoes_ciclo_atual
    if not acoes_atuais:
        raise RegraNegocioError("Cadastre ao menos uma ação corretiva antes de avançar", code="SEM_ACOES")
    if any(a.status != StatusAcaoCorretiva.CONCLUIDA for a in acoes_atuais):
        raise RegraNegocioError(
            "Todas as ações corretivas do ciclo atual devem estar 'Concluída' antes de avançar",
            code="ACOES_PENDENTES",
        )
    status_anterior = plano.status
    plano.status = StatusPlanoAcao.AGUARDANDO_VERIFICACAO
    plano_acao_repository.update(db, plano)
    auditoria_service.registrar(
        db,
        entidade="plano_acao",
        entidade_id=plano.id,
        acao="mudanca_status",
        usuario=usuario,
        detalhe=f"{status_anterior.value} -> {plano.status.value}",
    )
    return plano


def registrar_verificacao(
    db: Session, plano_id: int, dados: VerificacaoEficaciaCreate, usuario: Usuario
) -> PlanoDeAcao:
    plano = obter(db, plano_id)
    if plano.status != StatusPlanoAcao.AGUARDANDO_VERIFICACAO:
        raise RegraNegocioError(
            "Só é possível registrar verificação de eficácia com o plano 'Aguardando verificação'",
            code="PLANO_STATUS_INVALIDO",
        )
    _checar_usuario(db, dados.responsavel_id)

    verificacao = VerificacaoEficaciaPlano(
        plano_id=plano.id,
        ciclo=plano.ciclo,
        data_verificacao=dados.data_verificacao,
        responsavel_id=dados.responsavel_id,
        resultado=dados.resultado,
        observacoes=dados.observacoes,
    )
    plano_acao_repository.add_verificacao(db, verificacao)

    status_anterior = plano.status
    if dados.resultado == ResultadoVerificacao.EFICAZ:
        plano.status = StatusPlanoAcao.ENCERRADO
    else:
        plano.status = StatusPlanoAcao.REABERTO
        plano.ciclo += 1
    plano_acao_repository.update(db, plano)
    auditoria_service.registrar(
        db,
        entidade="plano_acao",
        entidade_id=plano.id,
        acao="mudanca_status",
        usuario=usuario,
        detalhe=f"{status_anterior.value} -> {plano.status.value} (verificação: {dados.resultado.value})",
    )
    return obter(db, plano.id)


def listar(db: Session, status: StatusPlanoAcao | None = None) -> list[PlanoDeAcao]:
    return plano_acao_repository.list_planos(db, status=status)


def indicadores(db: Session) -> dict:
    return plano_acao_repository.indicadores(db)


def to_list_item(plano: PlanoDeAcao) -> PlanoDeAcaoListItem:
    acoes = []
    for acao in plano.acoes_ciclo_atual:
        item = AcaoCorretivaRead.model_validate(acao)
        item.status = acao.status_calculado
        acoes.append(item)
    acoes.sort(key=lambda a: a.prazo)

    return PlanoDeAcaoListItem(
        id=plano.id,
        nc_id=plano.nc_id,
        numero_rnc=plano.nao_conformidade.numero_rnc,
        peca_codigo=plano.nao_conformidade.peca.codigo,
        peca_descricao=plano.nao_conformidade.peca.descricao,
        metodologia_causa_raiz=plano.metodologia_causa_raiz,
        status=plano.status,
        ciclo=plano.ciclo,
        acoes=acoes,
        total_acoes=len(acoes),
        acoes_concluidas=sum(1 for a in acoes if a.status == "concluida"),
        acoes_atrasadas=sum(1 for a in acoes if a.status == "atrasada"),
        proximo_prazo=min((a.prazo for a in acoes if a.status != "concluida"), default=None),
    )


def to_detalhe(db: Session, plano: PlanoDeAcao) -> PlanoDeAcaoDetalhe:
    detalhe = PlanoDeAcaoDetalhe.model_validate(plano)
    detalhe.numero_rnc = plano.nao_conformidade.numero_rnc
    detalhe.descricao_problema = plano.nao_conformidade.descricao_problema
    detalhe.acoes_corretivas = []
    for acao in plano.acoes_corretivas:
        item = AcaoCorretivaRead.model_validate(acao)
        item.status = acao.status_calculado
        detalhe.acoes_corretivas.append(item)
    detalhe.historico = [
        EventoHistorico(acao=log.acao, usuario_nome=log.usuario.nome, detalhe=log.detalhe, criado_em=log.criado_em)
        for log in listar_por_entidade(db, "plano_acao", plano.id)
    ]
    return detalhe
