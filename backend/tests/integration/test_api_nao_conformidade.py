import pytest

from app.core.permissions import Perfil


@pytest.fixture
def peca_pronta(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    peca = client.post(
        "/api/v1/pecas", json={"codigo": "RNC-001", "descricao": "Peça RNC", "revisao": "Rev. A"}, headers=headers
    ).json()
    return peca


def test_operador_pode_abrir_rnc(client, auth_headers, peca_pronta):
    headers = auth_headers(Perfil.OPERADOR)
    resposta = client.post(
        "/api/v1/nao-conformidades",
        json={
            "peca_id": peca_pronta["id"],
            "descricao_problema": "Peça fora de especificação",
            "quantidade_afetada": 2,
            "classificacao": "menor",
            "origem": "processo",
        },
        headers=headers,
    )
    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["numero_rnc"].startswith("RNC-")
    assert corpo["status"] == "aberta"
    assert corpo["aberto_por_nome"] == "user_operador"


def test_numeracao_rnc_sequencial(client, auth_headers, peca_pronta):
    headers = auth_headers(Perfil.OPERADOR)
    dados = {
        "peca_id": peca_pronta["id"],
        "descricao_problema": "Problema",
        "quantidade_afetada": 1,
        "classificacao": "menor",
        "origem": "processo",
    }
    nc1 = client.post("/api/v1/nao-conformidades", json=dados, headers=headers).json()
    nc2 = client.post("/api/v1/nao-conformidades", json=dados, headers=headers).json()
    seq1 = int(nc1["numero_rnc"].split("-")[-1])
    seq2 = int(nc2["numero_rnc"].split("-")[-1])
    assert seq2 == seq1 + 1


def test_rnc_sem_peca_e_rejeitada(client, auth_headers):
    headers = auth_headers(Perfil.OPERADOR)
    resposta = client.post(
        "/api/v1/nao-conformidades",
        json={"descricao_problema": "x", "quantidade_afetada": 1, "classificacao": "menor", "origem": "processo"},
        headers=headers,
    )
    assert resposta.status_code == 422  # peca_id obrigatório no schema


def test_operador_nao_pode_tratar_rnc(client, auth_headers, peca_pronta):
    headers_op = auth_headers(Perfil.OPERADOR)
    nc = client.post(
        "/api/v1/nao-conformidades",
        json={
            "peca_id": peca_pronta["id"],
            "descricao_problema": "Problema",
            "quantidade_afetada": 1,
            "classificacao": "menor",
            "origem": "processo",
        },
        headers=headers_op,
    ).json()

    resposta = client.patch(
        f"/api/v1/nao-conformidades/{nc['id']}/tratamento",
        json={"disposicao": "retrabalho", "necessita_plano_acao": False},
        headers=headers_op,
    )
    assert resposta.status_code == 403


def test_fluxo_tratamento_e_encerramento(client, auth_headers, peca_pronta):
    headers_op = auth_headers(Perfil.OPERADOR)
    headers_qual = auth_headers(Perfil.ANALISTA_QUALIDADE)

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
    assert nc["status"] == "aberta"

    # Não pode encerrar direto de "aberta".
    resposta = client.post(f"/api/v1/nao-conformidades/{nc['id']}/encerrar", headers=headers_qual)
    assert resposta.status_code == 400

    # Tratamento parcial (sem disposição) avança só até "em_analise".
    resposta = client.patch(
        f"/api/v1/nao-conformidades/{nc['id']}/tratamento",
        json={"responsavel_analise_id": None, "necessita_plano_acao": False},
        headers=headers_qual,
    )
    assert resposta.json()["status"] == "em_analise"

    # Preencher disposição avança para "em_tratamento" e cria plano de ação.
    analista_id = client.get("/api/v1/usuarios", headers=headers_qual).json()[0]["id"]
    resposta = client.patch(
        f"/api/v1/nao-conformidades/{nc['id']}/tratamento",
        json={
            "disposicao": "retrabalho",
            "responsavel_analise_id": analista_id,
            "necessita_plano_acao": True,
        },
        headers=headers_qual,
    )
    corpo = resposta.json()
    assert corpo["status"] == "em_tratamento"
    assert corpo["plano_acao_ativo_id"] is not None

    resposta = client.post(f"/api/v1/nao-conformidades/{nc['id']}/encerrar", headers=headers_qual)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "encerrada"
    # Plano de ação ainda aberto -> indicador de atenção deve estar ligado.
    assert corpo["tem_plano_aberto"] is True


def test_encerrar_rnc_ja_encerrada_conflita(client, auth_headers, peca_pronta):
    headers_op = auth_headers(Perfil.OPERADOR)
    headers_qual = auth_headers(Perfil.ANALISTA_QUALIDADE)
    nc = client.post(
        "/api/v1/nao-conformidades",
        json={
            "peca_id": peca_pronta["id"],
            "descricao_problema": "Problema",
            "quantidade_afetada": 1,
            "classificacao": "menor",
            "origem": "processo",
        },
        headers=headers_op,
    ).json()
    client.patch(
        f"/api/v1/nao-conformidades/{nc['id']}/tratamento",
        json={"disposicao": "sucata", "necessita_plano_acao": False},
        headers=headers_qual,
    )
    client.post(f"/api/v1/nao-conformidades/{nc['id']}/encerrar", headers=headers_qual)
    resposta = client.patch(
        f"/api/v1/nao-conformidades/{nc['id']}/tratamento",
        json={"necessita_plano_acao": False},
        headers=headers_qual,
    )
    assert resposta.status_code == 409


def test_listar_filtra_por_status(client, auth_headers, peca_pronta):
    headers_op = auth_headers(Perfil.OPERADOR)
    client.post(
        "/api/v1/nao-conformidades",
        json={
            "peca_id": peca_pronta["id"],
            "descricao_problema": "Problema",
            "quantidade_afetada": 1,
            "classificacao": "menor",
            "origem": "processo",
        },
        headers=headers_op,
    )
    resposta = client.get("/api/v1/nao-conformidades", params={"status": "aberta"}, headers=headers_op)
    assert resposta.status_code == 200
    assert len(resposta.json()) >= 1
    assert all(item["status"] == "aberta" for item in resposta.json())


def test_indicadores(client, auth_headers, peca_pronta):
    headers_op = auth_headers(Perfil.OPERADOR)
    client.post(
        "/api/v1/nao-conformidades",
        json={
            "peca_id": peca_pronta["id"],
            "descricao_problema": "Problema",
            "quantidade_afetada": 1,
            "classificacao": "menor",
            "origem": "processo",
        },
        headers=headers_op,
    )
    resposta = client.get("/api/v1/nao-conformidades/indicadores", headers=headers_op)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["abertas"] >= 1
