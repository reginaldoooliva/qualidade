from app.core.permissions import Perfil

DEPARTAMENTO_PAYLOAD = {"nome": "Engenharia"}


def test_operador_nao_pode_criar_departamento(client, auth_headers):
    headers = auth_headers(Perfil.OPERADOR)
    resposta = client.post("/api/v1/departamentos", json=DEPARTAMENTO_PAYLOAD, headers=headers)
    assert resposta.status_code == 403


def test_analista_pode_criar_departamento(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    resposta = client.post("/api/v1/departamentos", json=DEPARTAMENTO_PAYLOAD, headers=headers)
    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Engenharia"


def test_nao_permite_nome_duplicado(client, auth_headers):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    resposta1 = client.post("/api/v1/departamentos", json=DEPARTAMENTO_PAYLOAD, headers=headers)
    assert resposta1.status_code == 201

    resposta2 = client.post("/api/v1/departamentos", json=DEPARTAMENTO_PAYLOAD, headers=headers)
    assert resposta2.status_code == 400
    assert resposta2.json()["code"] == "NOME_DUPLICADO"


def test_listar_departamentos_requer_autenticacao(client):
    resposta = client.get("/api/v1/departamentos")
    assert resposta.status_code == 401


def test_gestor_pode_atribuir_departamento_a_usuario(client, auth_headers, db):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    depto = client.post("/api/v1/departamentos", json=DEPARTAMENTO_PAYLOAD, headers=headers).json()

    from app.core.security import hash_senha
    from app.models.usuario import Usuario

    usuario = Usuario(nome="Compras Um", login="compras1", senha_hash=hash_senha("senha123"), perfil=Perfil.OPERADOR)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    resposta = client.patch(
        f"/api/v1/usuarios/{usuario.id}/departamento", json={"departamento_id": depto["id"]}, headers=headers
    )
    assert resposta.status_code == 200
    assert resposta.json()["departamento_id"] == depto["id"]


def test_analista_nao_pode_atribuir_departamento(client, auth_headers, db):
    headers_gestor = auth_headers(Perfil.GESTOR_QUALIDADE)
    depto = client.post("/api/v1/departamentos", json=DEPARTAMENTO_PAYLOAD, headers=headers_gestor).json()

    headers_analista = auth_headers(Perfil.ANALISTA_QUALIDADE)
    resposta = client.patch(
        "/api/v1/usuarios/1/departamento", json={"departamento_id": depto["id"]}, headers=headers_analista
    )
    assert resposta.status_code == 403
