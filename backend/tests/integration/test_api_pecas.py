from app.core.permissions import Perfil

PECA_PAYLOAD = {
    "codigo": "TEST-001",
    "descricao": "Peça de teste",
    "revisao": "Rev. A",
}


def test_operador_nao_pode_criar_peca(client, auth_headers):
    headers = auth_headers(Perfil.OPERADOR)
    resposta = client.post("/api/v1/pecas", json=PECA_PAYLOAD, headers=headers)
    assert resposta.status_code == 403


def test_analista_pode_criar_peca(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    resposta = client.post("/api/v1/pecas", json=PECA_PAYLOAD, headers=headers)
    assert resposta.status_code == 201
    assert resposta.json()["codigo"] == "TEST-001"


def test_nao_permite_codigo_duplicado(client, auth_headers):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    resposta1 = client.post("/api/v1/pecas", json=PECA_PAYLOAD, headers=headers)
    assert resposta1.status_code == 201

    resposta2 = client.post("/api/v1/pecas", json=PECA_PAYLOAD, headers=headers)
    assert resposta2.status_code == 400
    assert resposta2.json()["code"] == "CODIGO_DUPLICADO"


def test_listar_pecas_requer_autenticacao(client):
    resposta = client.get("/api/v1/pecas")
    assert resposta.status_code == 401


def test_criar_etapa_e_caracteristica_calcula_lse_lie(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    peca = client.post("/api/v1/pecas", json=PECA_PAYLOAD, headers=headers).json()

    etapa = client.post(
        f"/api/v1/pecas/{peca['id']}/etapas",
        json={"numero_etapa": 10, "descricao": "Torneamento", "freq_numerador": 1, "freq_denominador": 10},
        headers=headers,
    ).json()
    assert etapa["numero_etapa"] == 10

    caracteristica = client.post(
        f"/api/v1/etapas/{etapa['id']}/caracteristicas",
        json={
            "nome": "Diâmetro externo",
            "nominal": 25.0,
            "tol_superior": 0.10,
            "tol_inferior": 0.02,
            "unidade": "mm",
        },
        headers=headers,
    ).json()

    assert caracteristica["lse"] == 25.10
    assert caracteristica["lie"] == 24.98


def test_nao_permite_etapa_numero_duplicado_na_mesma_peca(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    peca = client.post("/api/v1/pecas", json=PECA_PAYLOAD, headers=headers).json()

    payload_etapa = {"numero_etapa": 10, "freq_numerador": 1, "freq_denominador": 10}
    r1 = client.post(f"/api/v1/pecas/{peca['id']}/etapas", json=payload_etapa, headers=headers)
    assert r1.status_code == 201

    r2 = client.post(f"/api/v1/pecas/{peca['id']}/etapas", json=payload_etapa, headers=headers)
    assert r2.status_code == 400
    assert r2.json()["code"] == "ETAPA_NUMERO_DUPLICADO"


def test_nao_permite_lse_menor_igual_lie(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    peca = client.post("/api/v1/pecas", json=PECA_PAYLOAD, headers=headers).json()
    etapa = client.post(
        f"/api/v1/pecas/{peca['id']}/etapas",
        json={"numero_etapa": 10, "freq_numerador": 1, "freq_denominador": 10},
        headers=headers,
    ).json()

    resposta = client.post(
        f"/api/v1/etapas/{etapa['id']}/caracteristicas",
        json={"nome": "Cota inválida", "nominal": 25.0, "tol_superior": 0, "tol_inferior": 0},
        headers=headers,
    )
    assert resposta.status_code == 400
    assert resposta.json()["code"] == "TOLERANCIA_AUSENTE"
