import statistics
from datetime import date

from sqlalchemy.orm import Session

from app.models.coleta import RodadaColeta
from app.repositories import analise_repository, caracteristica_repository
from app.services import etapa_service, peca_service

# Constantes A2/D3/D4 para carta X-barra/R por tamanho de subgrupo (n=2..10) — tabela padrão de CEP.
CONSTANTES_CONTROLE: dict[int, tuple[float, float, float]] = {
    2: (1.880, 0.000, 3.267),
    3: (1.023, 0.000, 2.574),
    4: (0.729, 0.000, 2.282),
    5: (0.577, 0.000, 2.114),
    6: (0.483, 0.000, 2.004),
    7: (0.419, 0.076, 1.924),
    8: (0.373, 0.136, 1.864),
    9: (0.337, 0.184, 1.816),
    10: (0.308, 0.223, 1.777),
}


def _constantes(n_medio: float) -> tuple[float, float, float]:
    n = max(2, min(10, round(n_medio)))
    return CONSTANTES_CONTROLE[n]


def _montar_subgrupos(rodadas: list[RodadaColeta], valores_por_rodada: dict[int, list[float]]) -> list[dict]:
    subgrupos = []
    for rodada in rodadas:
        valores = valores_por_rodada.get(rodada.id, [])
        if len(valores) < 2:
            continue
        subgrupos.append(
            {
                "rodada_id": rodada.id,
                "numero_ordem": rodada.numero_ordem,
                "data_hora_inicio": rodada.data_hora_inicio,
                "n": len(valores),
                "media": statistics.fmean(valores),
                "amplitude": max(valores) - min(valores),
            }
        )
    return subgrupos


def calcular(
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
        medicoes = analise_repository.list_medicoes(db, rodada_ids, caracteristica.id, operador_id=operador_id)
        valores_por_rodada: dict[int, list[float]] = {}
        for medicao in medicoes:
            valores_por_rodada.setdefault(medicao.rodada_id, []).append(float(medicao.valor))

        subgrupos = _montar_subgrupos(rodadas, valores_por_rodada)
        exibir = len(subgrupos) >= 2

        tamanho_amostra_medio = None
        linha_central_x = lsc_x = lic_x = None
        linha_central_r = lsc_r = lic_r = None

        if exibir:
            tamanho_amostra_medio = statistics.fmean(s["n"] for s in subgrupos)
            a2, d3, d4 = _constantes(tamanho_amostra_medio)

            linha_central_x = statistics.fmean(s["media"] for s in subgrupos)
            linha_central_r = statistics.fmean(s["amplitude"] for s in subgrupos)
            lsc_x = linha_central_x + a2 * linha_central_r
            lic_x = linha_central_x - a2 * linha_central_r
            lsc_r = d4 * linha_central_r
            lic_r = d3 * linha_central_r

            for subgrupo in subgrupos:
                subgrupo["fora_controle_x"] = subgrupo["media"] > lsc_x or subgrupo["media"] < lic_x
                subgrupo["fora_controle_r"] = subgrupo["amplitude"] > lsc_r or subgrupo["amplitude"] < lic_r
        else:
            for subgrupo in subgrupos:
                subgrupo["fora_controle_x"] = False
                subgrupo["fora_controle_r"] = False

        resultados.append(
            {
                "caracteristica_id": caracteristica.id,
                "nome": caracteristica.nome,
                "unidade": caracteristica.unidade,
                "casas_decimais": caracteristica.casas_decimais,
                "subgrupos": subgrupos,
                "exibir": exibir,
                "tamanho_amostra_medio": tamanho_amostra_medio,
                "linha_central_x": linha_central_x,
                "lsc_x": lsc_x,
                "lic_x": lic_x,
                "linha_central_r": linha_central_r,
                "lsc_r": lsc_r,
                "lic_r": lic_r,
            }
        )

    return {
        "peca_id": peca.id,
        "peca_codigo": peca.codigo,
        "etapa_id": etapa.id,
        "etapa_numero": etapa.numero_etapa,
        "rodadas_incluidas": rodadas,
        "operadores_disponiveis": operadores,
        "caracteristicas": resultados,
    }
