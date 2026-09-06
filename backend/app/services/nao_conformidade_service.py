from datetime import date, datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflitoEstadoError, RecursoNaoEncontradoError, RegraNegocioError
from app.models.nao_conformidade import (
    ClassificacaoNC,
    NaoConformidade,
    OrigemNC,
    StatusNC,
)
from app.models.plano_acao import PlanoDeAcao
from app.models.usuario import Usuario
from app.repositories import (
    caracteristica_repository,
    coleta_repository,
    etapa_repository,
    nao_conformidade_repository,
    plano_acao_repository,
    producao_repository,
)
from app.schemas.nao_conformidade import (
    AbrirNCRequest,
    EventoHistorico,
    NaoConformidadeDetalhe,
    NaoConformidadeListItem,
    PlanoAcaoResumo,
    TratarNCRequest,
)
from app.services import auditoria_service, peca_service
from app.services.auditoria_service import listar_por_entidade


def _proximo_numero_rnc(db: Session) -> str:
    ano = date.today().year
    prefixo = f"RNC-{ano}-"
    ultimo = nao_conformidade_repository.get_ultimo_numero_do_ano(db, prefixo)
    proxima_seq = int(ultimo[len(prefixo) :]) + 1 if ultimo else 1
    return f"{prefixo}{proxima_seq:04d}"


def abrir(db: Session, dados: AbrirNCRequest, usuario: Usuario) -> NaoConformidade:
    peca = peca_service.obter(db, dados.peca_id)

    etapa = None
    if dados.etapa_id is not None:
        etapa = etapa_repository.get_by_id(db, dados.etapa_id)
        if not etapa or etapa.peca_id != peca.id:
            raise RecursoNaoEncontradoError("Etapa não encontrada para esta peça")

    caracteristica = None
    if dados.caracteristica_id is not None:
        caracteristica = caracteristica_repository.get_by_id(db, dados.caracteristica_id)
        if not caracteristica or (etapa is not None and caracteristica.etapa_id != etapa.id):
            raise RecursoNaoEncontradoError("Característica não encontrada para esta etapa")

    ordem = None
    if dados.ordem_id is not None:
        ordem = producao_repository.get_by_id(db, dados.ordem_id)
        if not ordem or ordem.peca_id != peca.id:
            raise RecursoNaoEncontradoError("Ordem não encontrada para esta peça")

    rodada = None
    if dados.rodada_id is not None:
        rodada = coleta_repository.get_by_id(db, dados.rodada_id)
        if not rodada:
            raise RecursoNaoEncontradoError("Rodada não encontrada")

    ultimo_erro = None
    for _ in range(5):
        nc = NaoConformidade(
            numero_rnc=_proximo_numero_rnc(db),
            peca_id=peca.id,
            ordem_id=ordem.id if ordem else None,
            etapa_id=etapa.id if etapa else None,
            caracteristica_id=caracteristica.id if caracteristica else None,
            rodada_id=rodada.id if rodada else None,
            descricao_problema=dados.descricao_problema,
            quantidade_afetada=dados.quantidade_afetada,
            classificacao=dados.classificacao,
            origem=dados.origem,
            aberto_por_id=usuario.id,
            status=StatusNC.ABERTA,
        )
        try:
            nc = nao_conformidade_repository.create(db, nc)
            break
        except IntegrityError as exc:
            db.rollback()
            ultimo_erro = exc
    else:
        raise ConflitoEstadoError(
            "Não foi possível gerar um número de RNC único; tente novamente",
            code="RNC_NUMERO_CONFLITO",
        ) from ultimo_erro
    auditoria_service.registrar(
        db, entidade="nao_conformidade", entidade_id=nc.id, acao="abertura", usuario=usuario,
        detalhe=f"RNC {nc.numero_rnc} aberta",
    )
    return nc


def obter(db: Session, nc_id: int) -> NaoConformidade:
    nc = nao_conformidade_repository.get_by_id(db, nc_id)
    if not nc:
        raise RecursoNaoEncontradoError(f"RNC {nc_id} não encontrada")
    return nc


def listar(
    db: Session,
    status: StatusNC | None = None,
    peca_id: int | None = None,
    classificacao: ClassificacaoNC | None = None,
    origem: OrigemNC | None = None,
    responsavel_analise_id: int | None = None,
    com_plano: bool | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> list[NaoConformidade]:
    return nao_conformidade_repository.list_nc(
        db,
        status=status,
        peca_id=peca_id,
        classificacao=classificacao,
        origem=origem,
        responsavel_analise_id=responsavel_analise_id,
        com_plano=com_plano,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


def tratar(db: Session, nc_id: int, dados: TratarNCRequest, usuario: Usuario) -> NaoConformidade:
    nc = obter(db, nc_id)
    if nc.status == StatusNC.ENCERRADA:
        raise ConflitoEstadoError("Esta RNC já está encerrada", code="RNC_ENCERRADA")

    status_anterior = nc.status
    if nc.status == StatusNC.ABERTA:
        nc.status = StatusNC.EM_ANALISE

    if dados.causa_raiz_preliminar is not None:
        nc.causa_raiz_preliminar = dados.causa_raiz_preliminar
    if dados.disposicao is not None:
        nc.disposicao = dados.disposicao
    if dados.responsavel_analise_id is not None:
        nc.responsavel_analise_id = dados.responsavel_analise_id
    if dados.necessita_plano_acao is not None:
        nc.necessita_plano_acao = dados.necessita_plano_acao

    if nc.disposicao is not None and nc.status == StatusNC.EM_ANALISE:
        nc.status = StatusNC.EM_TRATAMENTO

    nao_conformidade_repository.update(db, nc)

    if status_anterior != nc.status:
        auditoria_service.registrar(
            db,
            entidade="nao_conformidade",
            entidade_id=nc.id,
            acao="mudanca_status",
            usuario=usuario,
            detalhe=f"{status_anterior.value} -> {nc.status.value}",
        )

    if nc.necessita_plano_acao and plano_acao_repository.get_ativo_por_nc(db, nc.id) is None:
        plano = plano_acao_repository.create(db, PlanoDeAcao(nc_id=nc.id))
        auditoria_service.registrar(
            db,
            entidade="plano_acao",
            entidade_id=plano.id,
            acao="abertura",
            usuario=usuario,
            detalhe=f"originado da RNC {nc.numero_rnc}",
        )

    return obter(db, nc.id)


def encerrar(db: Session, nc_id: int, usuario: Usuario) -> NaoConformidade:
    nc = obter(db, nc_id)
    if nc.status != StatusNC.EM_TRATAMENTO:
        raise RegraNegocioError(
            "Só é possível encerrar uma RNC em tratamento, com a disposição da peça já definida",
            code="RNC_NAO_PRONTA_PARA_ENCERRAR",
        )
    nc.status = StatusNC.ENCERRADA
    nc.data_encerramento = datetime.now(timezone.utc)
    nao_conformidade_repository.update(db, nc)
    auditoria_service.registrar(
        db,
        entidade="nao_conformidade",
        entidade_id=nc.id,
        acao="encerramento",
        usuario=usuario,
        detalhe=f"RNC {nc.numero_rnc} encerrada",
    )
    return nc


def indicadores(db: Session) -> dict:
    return nao_conformidade_repository.indicadores(db)


def to_list_item(nc: NaoConformidade) -> NaoConformidadeListItem:
    item = NaoConformidadeListItem.model_validate(nc)
    item.peca_codigo = nc.peca.codigo
    item.peca_descricao = nc.peca.descricao
    plano_ativo = nc.plano_acao_ativo
    item.plano_acao_id = plano_ativo.id if plano_ativo else None
    item.plano_acao_status = plano_ativo.status.value if plano_ativo else None
    item.tem_plano_aberto = nc.tem_plano_aberto
    return item


def to_detalhe(db: Session, nc: NaoConformidade) -> NaoConformidadeDetalhe:
    detalhe = NaoConformidadeDetalhe.model_validate(nc)
    plano_ativo = nc.plano_acao_ativo
    detalhe.plano_acao_ativo_id = plano_ativo.id if plano_ativo else None
    detalhe.tem_plano_aberto = nc.tem_plano_aberto
    detalhe.planos_acao = [
        PlanoAcaoResumo(id=p.id, status=p.status.value, ciclo=p.ciclo) for p in nc.planos_acao
    ]
    detalhe.historico = [
        EventoHistorico(acao=log.acao, usuario_nome=log.usuario.nome, detalhe=log.detalhe, criado_em=log.criado_em)
        for log in listar_por_entidade(db, "nao_conformidade", nc.id)
    ]
    return detalhe
