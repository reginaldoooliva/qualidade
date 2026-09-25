from app.core.permissions import Perfil

FORNECEDOR_PAYLOAD = {"codigo": "FORN-001", "nome": "Fornecedor Teste", "cnpj": "00.000.000/0001-00"}


def test_operador_nao_pode_criar_fornecedor(client, auth_headers):
    headers = auth_headers(Perfil.OPERADOR)
    resposta = client.post("/api/v1/fornecedores", json=FORNECEDOR_PAYLOAD, headers=headers)
    assert resposta.status_code == 403


def test_analista_pode_criar_fornecedor(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    resposta = client.post("/api/v1/fornecedores", json=FORNECEDOR_PAYLOAD, headers=headers)
    assert resposta.status_code == 201
    assert resposta.json()["codigo"] == "FORN-001"


def test_nao_permite_codigo_duplicado(client, auth_headers):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    resposta1 = client.post("/api/v1/fornecedores", json=FORNECEDOR_PAYLOAD, headers=headers)
    assert resposta1.status_code == 201

    resposta2 = client.post("/api/v1/fornecedores", json=FORNECEDOR_PAYLOAD, headers=headers)
    assert resposta2.status_code == 400
    assert resposta2.json()["code"] == "CODIGO_DUPLICADO"


def test_listar_fornecedores_requer_autenticacao(client):
    resposta = client.get("/api/v1/fornecedores")
    assert resposta.status_code == 401


def test_inativar_e_ativar_fornecedor(client, auth_headers):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    fornecedor = client.post("/api/v1/fornecedores", json=FORNECEDOR_PAYLOAD, headers=headers).json()

    resposta = client.patch(f"/api/v1/fornecedores/{fornecedor['id']}/inativar", headers=headers)
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "inativo"

    resposta = client.patch(f"/api/v1/fornecedores/{fornecedor['id']}/ativar", headers=headers)
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "ativo"
