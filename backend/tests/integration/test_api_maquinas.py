from app.core.permissions import Perfil

MAQUINA_PAYLOAD = {"codigo": "MAQ-001", "descricao": "Torno CNC 1"}


def test_operador_nao_pode_criar_maquina(client, auth_headers):
    headers = auth_headers(Perfil.OPERADOR)
    resposta = client.post("/api/v1/maquinas", json=MAQUINA_PAYLOAD, headers=headers)
    assert resposta.status_code == 403


def test_analista_pode_criar_maquina(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    resposta = client.post("/api/v1/maquinas", json=MAQUINA_PAYLOAD, headers=headers)
    assert resposta.status_code == 201
    assert resposta.json()["codigo"] == "MAQ-001"


def test_nao_permite_codigo_duplicado(client, auth_headers):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    resposta1 = client.post("/api/v1/maquinas", json=MAQUINA_PAYLOAD, headers=headers)
    assert resposta1.status_code == 201

    resposta2 = client.post("/api/v1/maquinas", json=MAQUINA_PAYLOAD, headers=headers)
    assert resposta2.status_code == 400
    assert resposta2.json()["code"] == "CODIGO_DUPLICADO"


def test_listar_maquinas_requer_autenticacao(client):
    resposta = client.get("/api/v1/maquinas")
    assert resposta.status_code == 401
