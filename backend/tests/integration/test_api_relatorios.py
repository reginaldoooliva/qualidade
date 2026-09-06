from datetime import date, timedelta

import pytest

from app.core.permissions import Perfil


@pytest.fixture
def rodada_finalizada(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    peca = client.post(
        "/api/v1/pecas", json={"codigo": "REL-001", "descricao": "Peça relatório", "revisao": "Rev. A"}, headers=headers
    ).json()
    etapa = client.post(
        f"/api/v1/pecas/{peca['id']}/etapas",
        json={"numero_etapa": 10, "freq_numerador": 1, "freq_denominador": 1},
        headers=headers,
    ).json()
    caracteristica = client.post(
        f"/api/v1/etapas/{etapa['id']}/caracteristicas",
        json={"nome": "Diâmetro", "nominal": 10.0, "tol_superior": 5.0, "tol_inferior": 5.0, "unidade": "mm"},
        headers=headers,
    ).json()

    headers_operador = auth_headers(Perfil.OPERADOR)
    rodada = client.post(
        "/api/v1/coletas/iniciar",
        json={"peca_id": peca["id"], "numero_ordem": "OP-R1", "quantidade_ordem": 3, "etapa_id": etapa["id"]},
        headers=headers_operador,
    ).json()
    for amostra, valor in enumerate([9.0, 10.0, 11.0], start=1):
        client.put(
            f"/api/v1/coletas/{rodada['id']}/medicoes/{caracteristica['id']}/{amostra}",
            json={"valor": valor},
            headers=headers_operador,
        )
    client.post(f"/api/v1/coletas/{rodada['id']}/finalizar", json={}, headers=headers_operador)

    return {"peca": peca, "etapa": etapa, "caracteristica": caracteristica, "rodada": rodada}


def test_relatorio_cpk_peca_pdf(client, auth_headers, rodada_finalizada):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    peca_id = rodada_finalizada["peca"]["id"]

    resposta = client.get(f"/api/v1/relatorios/pecas/{peca_id}/cpk", headers=headers)
    assert resposta.status_code == 200
    assert resposta.headers["content-type"] == "application/pdf"
    assert resposta.content[:4] == b"%PDF"
    assert len(resposta.content) > 500


def test_relatorio_dados_brutos_xlsx(client, auth_headers, rodada_finalizada):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    peca_id = rodada_finalizada["peca"]["id"]

    resposta = client.get(f"/api/v1/relatorios/pecas/{peca_id}/dados-brutos", headers=headers)
    assert resposta.status_code == 200
    assert "spreadsheetml" in resposta.headers["content-type"]
    assert resposta.content[:2] == b"PK"  # assinatura de arquivo zip (xlsx)


def test_relatorio_consolidado_pecas_calcula_pior_cpk(client, auth_headers, rodada_finalizada):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)

    resposta = client.get("/api/v1/relatorios/pecas/consolidado", headers=headers)
    assert resposta.status_code == 200
    itens = resposta.json()
    item = next(i for i in itens if i["codigo"] == "REL-001")
    # LIE=5, LSE=15, valores 9/10/11 -> média 10, desvio 1, Cpk = 10/6
    assert item["cpk_critico"] == pytest.approx(10 / 6)
    assert item["caracteristica_critica"] == "Diâmetro"
    assert item["classificacao"] == "capaz"


def test_relatorio_consolidado_pecas_bloqueado_para_analista(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    resposta = client.get("/api/v1/relatorios/pecas/consolidado", headers=headers)
    assert resposta.status_code == 403


def test_relatorio_consolidado_pecas_pdf(client, auth_headers, rodada_finalizada):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    resposta = client.get("/api/v1/relatorios/pecas/consolidado/pdf", headers=headers)
    assert resposta.status_code == 200
    assert resposta.content[:4] == b"%PDF"


@pytest.fixture
def rnc_com_plano_reaberto(client, auth_headers):
    headers_op = auth_headers(Perfil.OPERADOR)
    headers_qual = auth_headers(Perfil.ANALISTA_QUALIDADE)

    peca = client.post(
        "/api/v1/pecas", json={"codigo": "REL-002", "descricao": "Peça RNC relatório", "revisao": "Rev. A"}, headers=headers_qual
    ).json()
    nc = client.post(
        "/api/v1/nao-conformidades",
        json={
            "peca_id": peca["id"],
            "descricao_problema": "Problema para relatório",
            "quantidade_afetada": 2,
            "classificacao": "maior",
            "origem": "processo",
        },
        headers=headers_op,
    ).json()
    nc = client.patch(
        f"/api/v1/nao-conformidades/{nc['id']}/tratamento",
        json={"disposicao": "retrabalho", "necessita_plano_acao": True},
        headers=headers_qual,
    ).json()
    plano_id = nc["plano_acao_ativo_id"]
    responsavel_id = client.get("/api/v1/usuarios", headers=headers_qual).json()[0]["id"]

    acao = client.post(
        f"/api/v1/planos-acao/{plano_id}/acoes",
        json={"descricao": "Ação 1", "responsavel_id": responsavel_id, "prazo": str(date.today() + timedelta(days=5))},
        headers=headers_qual,
    ).json()["acoes_corretivas"][0]
    client.patch(f"/api/v1/planos-acao/{plano_id}/acoes/{acao['id']}/concluir", headers=headers_qual)
    client.post(f"/api/v1/planos-acao/{plano_id}/avancar-verificacao", headers=headers_qual)
    client.post(
        f"/api/v1/planos-acao/{plano_id}/verificacao",
        json={"data_verificacao": str(date.today()), "responsavel_id": responsavel_id, "resultado": "nao_eficaz"},
        headers=headers_qual,
    )
    client.post(f"/api/v1/nao-conformidades/{nc['id']}/encerrar", headers=headers_qual)

    return {"nc_id": nc["id"], "peca": peca}


def test_relatorio_rnc_pdf(client, auth_headers, rnc_com_plano_reaberto):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    nc_id = rnc_com_plano_reaberto["nc_id"]

    resposta = client.get(f"/api/v1/relatorios/nao-conformidades/{nc_id}", headers=headers)
    assert resposta.status_code == 200
    assert resposta.content[:4] == b"%PDF"


def test_relatorio_consolidado_nc(client, auth_headers, rnc_com_plano_reaberto):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)

    resposta = client.get("/api/v1/relatorios/nao-conformidades/consolidado", headers=headers)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total_rnc"] >= 1
    assert corpo["total_encerradas"] >= 1
    assert corpo["tempo_medio_tratamento_dias"] is not None
    assert corpo["tempo_medio_tratamento_dias"] >= 0
    # o único plano criado nesse fluxo foi reaberto (verificação "não eficaz") -> ciclo 2 -> reincidência 100%
    peca_codigo_key = next(k for k in corpo["por_peca"] if k.startswith("REL-002"))
    assert corpo["por_peca"][peca_codigo_key] == 1
    assert corpo["taxa_reincidencia"] == pytest.approx(1.0)


def test_relatorio_consolidado_nc_bloqueado_para_operador(client, auth_headers):
    headers = auth_headers(Perfil.OPERADOR)
    resposta = client.get("/api/v1/relatorios/nao-conformidades/consolidado", headers=headers)
    assert resposta.status_code == 403


def test_relatorio_consolidado_nc_pdf(client, auth_headers, rnc_com_plano_reaberto):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    resposta = client.get("/api/v1/relatorios/nao-conformidades/consolidado/pdf", headers=headers)
    assert resposta.status_code == 200
    assert resposta.content[:4] == b"%PDF"
