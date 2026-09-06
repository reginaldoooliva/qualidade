import pytest

from app.core.permissions import Perfil


@pytest.fixture
def rodada_finalizada(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    peca = client.post(
        "/api/v1/pecas", json={"codigo": "ANL-001", "descricao": "Peça análise", "revisao": "Rev. A"}, headers=headers
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
        json={"peca_id": peca["id"], "numero_ordem": "OP-A1", "quantidade_ordem": 3, "etapa_id": etapa["id"]},
        headers=headers_operador,
    ).json()

    # LIE=5, LSE=15 (nominal 10 +-5); valores 9, 10, 11 -> média 10, desvio amostral 1, Cp=Cpk=10/6
    for amostra, valor in enumerate([9.0, 10.0, 11.0], start=1):
        client.put(
            f"/api/v1/coletas/{rodada['id']}/medicoes/{caracteristica['id']}/{amostra}",
            json={"valor": valor},
            headers=headers_operador,
        )
    client.post(f"/api/v1/coletas/{rodada['id']}/finalizar", json={}, headers=headers_operador)

    return {"peca": peca, "etapa": etapa, "caracteristica": caracteristica, "rodada": rodada}


def test_analise_calcula_cpk_corretamente(client, auth_headers, rodada_finalizada):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    peca_id = rodada_finalizada["peca"]["id"]
    etapa_id = rodada_finalizada["etapa"]["id"]

    resposta = client.get(f"/api/v1/analise/pecas/{peca_id}/etapas/{etapa_id}/capabilidade", headers=headers)
    assert resposta.status_code == 200
    corpo = resposta.json()

    assert len(corpo["caracteristicas"]) == 1
    resultado = corpo["caracteristicas"][0]
    assert resultado["n_amostras"] == 3
    assert resultado["media"] == pytest.approx(10.0)
    assert resultado["desvio_padrao"] == pytest.approx(1.0)
    assert resultado["cp"] == pytest.approx(10 / 6)
    assert resultado["cpk"] == pytest.approx(10 / 6)
    assert resultado["classificacao"] == "capaz"
    assert resultado["baixa_robustez"] is True
    assert sorted(resultado["valores"]) == [9.0, 10.0, 11.0]
    assert len(corpo["rodadas_incluidas"]) == 1
    assert corpo["rodadas_incluidas"][0]["id"] == rodada_finalizada["rodada"]["id"]


def test_analise_exclui_rodada_em_andamento(client, auth_headers, rodada_finalizada):
    headers_operador = auth_headers(Perfil.OPERADOR)
    peca_id = rodada_finalizada["peca"]["id"]
    etapa_id = rodada_finalizada["etapa"]["id"]

    # nova rodada em_andamento (não deve entrar na análise)
    client.post(
        "/api/v1/coletas/iniciar",
        json={"peca_id": peca_id, "numero_ordem": "OP-A2", "quantidade_ordem": 3, "etapa_id": etapa_id},
        headers=headers_operador,
    )

    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    resposta = client.get(f"/api/v1/analise/pecas/{peca_id}/etapas/{etapa_id}/capabilidade", headers=headers)
    corpo = resposta.json()
    assert len(corpo["rodadas_incluidas"]) == 1  # só a finalizada


def test_analise_filtro_por_rodada_especifica(client, auth_headers, rodada_finalizada):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    peca_id = rodada_finalizada["peca"]["id"]
    etapa_id = rodada_finalizada["etapa"]["id"]
    rodada_id = rodada_finalizada["rodada"]["id"]

    resposta = client.get(
        f"/api/v1/analise/pecas/{peca_id}/etapas/{etapa_id}/capabilidade",
        params={"rodada_id": rodada_id},
        headers=headers,
    )
    assert resposta.status_code == 200
    assert resposta.json()["caracteristicas"][0]["n_amostras"] == 3

    resposta_outra = client.get(
        f"/api/v1/analise/pecas/{peca_id}/etapas/{etapa_id}/capabilidade",
        params={"rodada_id": rodada_id + 999},
        headers=headers,
    )
    assert resposta_outra.json()["caracteristicas"][0]["n_amostras"] == 0


def test_analise_sem_dados_retorna_zero_amostras(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    peca = client.post(
        "/api/v1/pecas", json={"codigo": "ANL-002", "descricao": "Peça sem coleta", "revisao": "Rev. A"}, headers=headers
    ).json()
    etapa = client.post(
        f"/api/v1/pecas/{peca['id']}/etapas",
        json={"numero_etapa": 10, "freq_numerador": 1, "freq_denominador": 1},
        headers=headers,
    ).json()
    client.post(
        f"/api/v1/etapas/{etapa['id']}/caracteristicas",
        json={"nome": "Diâmetro", "nominal": 10.0, "tol_superior": 5.0, "tol_inferior": 5.0, "unidade": "mm"},
        headers=headers,
    )

    resposta = client.get(f"/api/v1/analise/pecas/{peca['id']}/etapas/{etapa['id']}/capabilidade", headers=headers)
    assert resposta.status_code == 200
    resultado = resposta.json()["caracteristicas"][0]
    assert resultado["n_amostras"] == 0
    assert resultado["cp"] is None
