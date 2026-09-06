import pytest

from app.core.permissions import Perfil


@pytest.fixture
def peca_etapa_caracteristica(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    peca = client.post(
        "/api/v1/pecas", json={"codigo": "CC-001", "descricao": "Peça carta", "revisao": "Rev. A"}, headers=headers
    ).json()
    etapa = client.post(
        f"/api/v1/pecas/{peca['id']}/etapas",
        json={"numero_etapa": 10, "freq_numerador": 1, "freq_denominador": 1},
        headers=headers,
    ).json()
    caracteristica = client.post(
        f"/api/v1/etapas/{etapa['id']}/caracteristicas",
        json={"nome": "Diâmetro", "nominal": 10.0, "tol_superior": 10.0, "tol_inferior": 10.0, "unidade": "mm"},
        headers=headers,
    ).json()
    return {"peca": peca, "etapa": etapa, "caracteristica": caracteristica}


@pytest.fixture
def tres_rodadas(client, auth_headers, peca_etapa_caracteristica):
    headers_operador = auth_headers(Perfil.OPERADOR)
    peca_id = peca_etapa_caracteristica["peca"]["id"]
    etapa_id = peca_etapa_caracteristica["etapa"]["id"]
    caracteristica_id = peca_etapa_caracteristica["caracteristica"]["id"]

    conjuntos = {
        "OP-C1": [10.0, 12.0, 14.0],  # média 12, amplitude 4
        "OP-C2": [11.0, 13.0, 15.0],  # média 13, amplitude 4
        "OP-C3": [9.0, 11.0, 13.0],  # média 11, amplitude 4
    }
    rodadas = []
    for numero_ordem, valores in conjuntos.items():
        rodada = client.post(
            "/api/v1/coletas/iniciar",
            json={
                "peca_id": peca_id,
                "numero_ordem": numero_ordem,
                "quantidade_ordem": 3,
                "etapa_id": etapa_id,
                "amostras_ajustadas": 3,
            },
            headers=headers_operador,
        ).json()
        for amostra, valor in enumerate(valores, start=1):
            client.put(
                f"/api/v1/coletas/{rodada['id']}/medicoes/{caracteristica_id}/{amostra}",
                json={"valor": valor},
                headers=headers_operador,
            )
        client.post(f"/api/v1/coletas/{rodada['id']}/finalizar", json={}, headers=headers_operador)
        rodadas.append(rodada)

    return {**peca_etapa_caracteristica, "rodadas": rodadas}


def test_carta_controle_calcula_limites_corretamente(client, auth_headers, tres_rodadas):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    peca_id = tres_rodadas["peca"]["id"]
    etapa_id = tres_rodadas["etapa"]["id"]

    resposta = client.get(f"/api/v1/analise/pecas/{peca_id}/etapas/{etapa_id}/carta-controle", headers=headers)
    assert resposta.status_code == 200
    corpo = resposta.json()

    assert len(corpo["caracteristicas"]) == 1
    resultado = corpo["caracteristicas"][0]
    assert resultado["exibir"] is True
    assert len(resultado["subgrupos"]) == 3

    # X-barra-barra = média(12,13,11) = 12; R-barra = média(4,4,4) = 4; n=3 -> A2=1.023, D4=2.574, D3=0
    assert resultado["linha_central_x"] == pytest.approx(12.0)
    assert resultado["linha_central_r"] == pytest.approx(4.0)
    assert resultado["lsc_x"] == pytest.approx(12.0 + 1.023 * 4.0)
    assert resultado["lic_x"] == pytest.approx(12.0 - 1.023 * 4.0)
    assert resultado["lsc_r"] == pytest.approx(2.574 * 4.0)
    assert resultado["lic_r"] == pytest.approx(0.0)

    for subgrupo in resultado["subgrupos"]:
        assert subgrupo["fora_controle_x"] is False
        assert subgrupo["fora_controle_r"] is False


def test_carta_controle_nao_exibe_com_menos_de_duas_rodadas(client, auth_headers, peca_etapa_caracteristica):
    headers_operador = auth_headers(Perfil.OPERADOR)
    peca_id = peca_etapa_caracteristica["peca"]["id"]
    etapa_id = peca_etapa_caracteristica["etapa"]["id"]
    caracteristica_id = peca_etapa_caracteristica["caracteristica"]["id"]

    rodada = client.post(
        "/api/v1/coletas/iniciar",
        json={
            "peca_id": peca_id,
            "numero_ordem": "OP-UNICA",
            "quantidade_ordem": 3,
            "etapa_id": etapa_id,
            "amostras_ajustadas": 3,
        },
        headers=headers_operador,
    ).json()
    for amostra, valor in enumerate([10.0, 11.0, 12.0], start=1):
        client.put(
            f"/api/v1/coletas/{rodada['id']}/medicoes/{caracteristica_id}/{amostra}",
            json={"valor": valor},
            headers=headers_operador,
        )
    client.post(f"/api/v1/coletas/{rodada['id']}/finalizar", json={}, headers=headers_operador)

    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    resposta = client.get(f"/api/v1/analise/pecas/{peca_id}/etapas/{etapa_id}/carta-controle", headers=headers)
    resultado = resposta.json()["caracteristicas"][0]
    assert resultado["exibir"] is False
    assert resultado["linha_central_x"] is None


def test_carta_controle_ponto_fora_de_controle(client, auth_headers, tres_rodadas):
    headers_operador = auth_headers(Perfil.OPERADOR)
    peca_id = tres_rodadas["peca"]["id"]
    etapa_id = tres_rodadas["etapa"]["id"]
    caracteristica_id = tres_rodadas["caracteristica"]["id"]

    # quarta rodada com média muito fora do padrão das outras três (10, 11, 12 -> 13, 13, 13 normal;
    # aqui usamos valores bem afastados para forçar média fora do LSC calculado a partir das 3 primeiras)
    rodada = client.post(
        "/api/v1/coletas/iniciar",
        json={
            "peca_id": peca_id,
            "numero_ordem": "OP-C4",
            "quantidade_ordem": 3,
            "etapa_id": etapa_id,
            "amostras_ajustadas": 3,
        },
        headers=headers_operador,
    ).json()
    for amostra, valor in enumerate([50.0, 52.0, 54.0], start=1):
        client.put(
            f"/api/v1/coletas/{rodada['id']}/medicoes/{caracteristica_id}/{amostra}",
            json={"valor": valor},
            headers=headers_operador,
        )
    client.post(f"/api/v1/coletas/{rodada['id']}/finalizar", json={}, headers=headers_operador)

    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    resposta = client.get(f"/api/v1/analise/pecas/{peca_id}/etapas/{etapa_id}/carta-controle", headers=headers)
    resultado = resposta.json()["caracteristicas"][0]
    assert len(resultado["subgrupos"]) == 4
    ultimo = resultado["subgrupos"][-1]
    assert ultimo["numero_ordem"] == "OP-C4"
    assert ultimo["fora_controle_x"] is True
