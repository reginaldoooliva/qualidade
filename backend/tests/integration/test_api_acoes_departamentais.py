import pytest

from app.core.permissions import Perfil
from app.core.security import hash_senha
from app.models.usuario import Usuario


@pytest.fixture
def peca_pronta(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    peca = client.post(
        "/api/v1/pecas", json={"codigo": "ACD-001", "descricao": "Peça tratativa", "revisao": "Rev. A"}, headers=headers
    ).json()
    return peca


def _abrir_e_tratar_com_sucata(client, peca_pronta, headers_op, headers_qual):
    nc = client.post(
        "/api/v1/nao-conformidades",
        json={
            "peca_id": peca_pronta["id"],
            "descricao_problema": "Problema",
            "quantidade_afetada": 1,
            "classificacao": "maior",
            "origem": "processo",
        },
        headers=headers_op,
    ).json()
    resposta = client.patch(
        f"/api/v1/nao-conformidades/{nc['id']}/tratamento",
        json={"disposicao": "sucata", "necessita_plano_acao": False},
        headers=headers_qual,
    )
    assert resposta.json()["status"] == "em_tratamento"
    return nc


def _criar_usuario_departamento(db, login: str, departamento_id: int) -> Usuario:
    usuario = Usuario(
        nome=login, login=login, senha_hash=hash_senha("senha123"), perfil=Perfil.OPERADOR, departamento_id=departamento_id
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def test_fluxo_completo_tratativa_bloqueia_e_libera_encerramento(client, auth_headers, db, peca_pronta):
    headers_op = auth_headers(Perfil.OPERADOR)
    headers_qual = auth_headers(Perfil.ANALISTA_QUALIDADE)

    pcp = client.post("/api/v1/departamentos", json={"nome": "PCP"}, headers=headers_qual).json()
    nc = _abrir_e_tratar_com_sucata(client, peca_pronta, headers_op, headers_qual)

    resposta = client.post(
        f"/api/v1/nao-conformidades/{nc['id']}/acoes-departamentais",
        json={"departamento_id": pcp["id"], "descricao": "Dar baixa da peça sucateada na ordem"},
        headers=headers_qual,
    )
    assert resposta.status_code == 201, resposta.text
    acao = resposta.json()
    assert acao["status"] == "pendente"
    assert acao["departamento"]["nome"] == "PCP"

    # Encerrar sem resolver a tratativa deve ser bloqueado.
    resposta = client.post(f"/api/v1/nao-conformidades/{nc['id']}/encerrar", headers=headers_qual)
    assert resposta.status_code == 409
    assert resposta.json()["code"] == "ACOES_DEPARTAMENTAIS_PENDENTES"

    # Usuário sem o departamento certo não pode concluir.
    resposta = client.patch(
        f"/api/v1/nao-conformidades/{nc['id']}/acoes-departamentais/{acao['id']}/concluir",
        json={"observacao": "tentativa indevida"},
        headers=headers_op,
    )
    assert resposta.status_code == 403

    # Usuário do departamento PCP conclui.
    usuario_pcp = _criar_usuario_departamento(db, "usuario_pcp", pcp["id"])
    login_resp = client.post("/api/v1/auth/login", json={"login": "usuario_pcp", "senha": "senha123"})
    headers_pcp = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    resposta = client.patch(
        f"/api/v1/nao-conformidades/{nc['id']}/acoes-departamentais/{acao['id']}/concluir",
        json={"observacao": "Baixa registrada na OP-1234"},
        headers=headers_pcp,
    )
    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["status"] == "concluida"
    assert corpo["observacao_conclusao"] == "Baixa registrada na OP-1234"
    assert corpo["concluido_por_nome"] == usuario_pcp.nome

    # Agora encerra normalmente.
    resposta = client.post(f"/api/v1/nao-conformidades/{nc['id']}/encerrar", headers=headers_qual)
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "encerrada"


def test_operador_nao_pode_criar_ou_remover_acao_departamental(client, auth_headers, peca_pronta):
    headers_op = auth_headers(Perfil.OPERADOR)
    headers_qual = auth_headers(Perfil.ANALISTA_QUALIDADE)
    pcp = client.post("/api/v1/departamentos", json={"nome": "PCP"}, headers=headers_qual).json()
    nc = _abrir_e_tratar_com_sucata(client, peca_pronta, headers_op, headers_qual)

    resposta = client.post(
        f"/api/v1/nao-conformidades/{nc['id']}/acoes-departamentais",
        json={"departamento_id": pcp["id"], "descricao": "x"},
        headers=headers_op,
    )
    assert resposta.status_code == 403

    acao = client.post(
        f"/api/v1/nao-conformidades/{nc['id']}/acoes-departamentais",
        json={"departamento_id": pcp["id"], "descricao": "x"},
        headers=headers_qual,
    ).json()
    resposta = client.delete(
        f"/api/v1/nao-conformidades/{nc['id']}/acoes-departamentais/{acao['id']}", headers=headers_op
    )
    assert resposta.status_code == 403


def test_nao_permite_remover_acao_ja_concluida(client, auth_headers, db, peca_pronta):
    headers_op = auth_headers(Perfil.OPERADOR)
    headers_qual = auth_headers(Perfil.ANALISTA_QUALIDADE)
    pcp = client.post("/api/v1/departamentos", json={"nome": "PCP"}, headers=headers_qual).json()
    nc = _abrir_e_tratar_com_sucata(client, peca_pronta, headers_op, headers_qual)
    acao = client.post(
        f"/api/v1/nao-conformidades/{nc['id']}/acoes-departamentais",
        json={"departamento_id": pcp["id"], "descricao": "x"},
        headers=headers_qual,
    ).json()

    # Qualidade também pode concluir diretamente.
    resposta = client.patch(
        f"/api/v1/nao-conformidades/{nc['id']}/acoes-departamentais/{acao['id']}/concluir",
        json={"observacao": "feito"},
        headers=headers_qual,
    )
    assert resposta.status_code == 200

    resposta = client.delete(
        f"/api/v1/nao-conformidades/{nc['id']}/acoes-departamentais/{acao['id']}", headers=headers_qual
    )
    assert resposta.status_code == 400
    assert resposta.json()["code"] == "ACAO_DEPARTAMENTAL_JA_CONCLUIDA"


def test_encerrar_com_ignorar_pendencias_forca_fechamento(client, auth_headers, peca_pronta):
    headers_op = auth_headers(Perfil.OPERADOR)
    headers_qual = auth_headers(Perfil.ANALISTA_QUALIDADE)
    pcp = client.post("/api/v1/departamentos", json={"nome": "PCP"}, headers=headers_qual).json()
    nc = _abrir_e_tratar_com_sucata(client, peca_pronta, headers_op, headers_qual)
    client.post(
        f"/api/v1/nao-conformidades/{nc['id']}/acoes-departamentais",
        json={"departamento_id": pcp["id"], "descricao": "x"},
        headers=headers_qual,
    )

    resposta = client.post(
        f"/api/v1/nao-conformidades/{nc['id']}/encerrar",
        params={"ignorar_pendencias": True},
        headers=headers_qual,
    )
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "encerrada"


def test_listar_pendentes_filtra_por_departamento_do_usuario(client, auth_headers, db, peca_pronta):
    headers_op = auth_headers(Perfil.OPERADOR)
    headers_qual = auth_headers(Perfil.ANALISTA_QUALIDADE)
    pcp = client.post("/api/v1/departamentos", json={"nome": "PCP"}, headers=headers_qual).json()
    compras = client.post(
        "/api/v1/departamentos", json={"nome": "Compras"}, headers=headers_qual
    ).json()
    nc = _abrir_e_tratar_com_sucata(client, peca_pronta, headers_op, headers_qual)
    client.post(
        f"/api/v1/nao-conformidades/{nc['id']}/acoes-departamentais",
        json={"departamento_id": pcp["id"], "descricao": "para o pcp"},
        headers=headers_qual,
    )
    client.post(
        f"/api/v1/nao-conformidades/{nc['id']}/acoes-departamentais",
        json={"departamento_id": compras["id"], "descricao": "para compras"},
        headers=headers_qual,
    )

    usuario_pcp = _criar_usuario_departamento(db, "usuario_pcp5", pcp["id"])
    login_resp = client.post("/api/v1/auth/login", json={"login": "usuario_pcp5", "senha": "senha123"})
    headers_pcp = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    resposta = client.get("/api/v1/acoes-departamentais", headers=headers_pcp)
    assert resposta.status_code == 200
    itens = resposta.json()
    assert len(itens) == 1
    assert itens[0]["descricao"] == "para o pcp"

    # Qualidade vê tudo por padrão.
    resposta = client.get("/api/v1/acoes-departamentais", headers=headers_qual)
    descricoes = {item["descricao"] for item in resposta.json()}
    assert "para o pcp" in descricoes
    assert "para compras" in descricoes
