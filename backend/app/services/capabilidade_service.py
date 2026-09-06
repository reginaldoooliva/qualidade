import statistics
from datetime import date

from sqlalchemy.orm import Session

from app.config import get_settings
from app.repositories import analise_repository, caracteristica_repository
from app.services import etapa_service, peca_service

settings = get_settings()


def classificar_cpk(cpk: float) -> str:
    if cpk < settings.cpk_limiar_nao_capaz:
        return "nao_capaz"
    if cpk <= settings.cpk_limiar_capaz:
        return "atencao"
    return "capaz"


def calcular_estatisticas(valores: list[float], lie: float, lse: float) -> dict:
    n = len(valores)
    if n == 0:
        return {
            "n_amostras": 0,
            "media": None,
            "desvio_padrao": None,
            "cp": None,
            "cpk": None,
            "classificacao": None,
            "baixa_robustez": False,
        }

    media = statistics.fmean(valores)

    if n < 2:
        return {
            "n_amostras": n,
            "media": media,
            "desvio_padrao": None,
            "cp": None,
            "cpk": None,
            "classificacao": None,
            "baixa_robustez": True,
        }

    desvio = statistics.stdev(valores)  # amostral (n-1)

    if desvio == 0:
        # sem variação nas amostras: Cp/Cpk tendem a infinito — não há como classificar de forma útil.
        return {
            "n_amostras": n,
            "media": media,
            "desvio_padrao": 0.0,
            "cp": None,
            "cpk": None,
            "classificacao": None,
            "baixa_robustez": n < settings.cpk_limiar_baixa_robustez,
        }

    cp = (lse - lie) / (6 * desvio)
    cpk = min((lse - media) / (3 * desvio), (media - lie) / (3 * desvio))

    return {
        "n_amostras": n,
        "media": media,
        "desvio_padrao": desvio,
        "cp": cp,
        "cpk": cpk,
        "classificacao": classificar_cpk(cpk),
        "baixa_robustez": n < settings.cpk_limiar_baixa_robustez,
    }


def analisar(
    db: Session,
    peca_id: int,
    etapa_id: int,
    rodada_id: int | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    operador_id: int | None = None,
) -> dict:
    peca = peca_service.obter(db, peca_id)
    etapa = etapa_service.obter(db, etapa_id)

    rodadas = analise_repository.list_rodadas_para_analise(
        db, peca_id, etapa_id, rodada_id=rodada_id, data_inicio=data_inicio, data_fim=data_fim
    )
    rodada_ids = [r.id for r in rodadas]

    operadores = analise_repository.list_operadores_das_rodadas(db, rodada_ids)
    caracteristicas = caracteristica_repository.list_by_etapa(db, etapa_id)

    resultados = []
    for caracteristica in caracteristicas:
        medicoes = analise_repository.list_medicoes(
            db, rodada_ids, caracteristica.id, operador_id=operador_id
        )
        valores = [float(m.valor) for m in medicoes]
        estatisticas = calcular_estatisticas(valores, caracteristica.lie, caracteristica.lse)
        resultados.append(
            {
                "caracteristica_id": caracteristica.id,
                "nome": caracteristica.nome,
                "unidade": caracteristica.unidade,
                "instrumento": caracteristica.instrumento,
                "casas_decimais": caracteristica.casas_decimais,
                "nominal": float(caracteristica.nominal),
                "lie": caracteristica.lie,
                "lse": caracteristica.lse,
                "valores": valores,
                **estatisticas,
            }
        )

    return {
        "peca_id": peca.id,
        "peca_codigo": peca.codigo,
        "etapa_id": etapa.id,
        "etapa_numero": etapa.numero_etapa,
        "rodadas_incluidas": rodadas,
        "operadores_disponiveis": operadores,
        "limiar_baixa_robustez": settings.cpk_limiar_baixa_robustez,
        "caracteristicas": resultados,
    }
