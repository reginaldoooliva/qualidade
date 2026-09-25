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


def test_abrir_rnc_tipo_fornecedor_sem_fornecedor_id_e_rejeitada(client, auth_headers, peca_pronta):
    headers = auth_headers(Perfil.OPERADOR)
    resposta = client.post(
        "/api/v1/nao-conformidades",
        json={
            "tipo": "fornecedor",
            "peca_id": peca_pronta["id"],
            "descricao_problema": "Lote recebido fora de especificação",
            "quantidade_afetada": 5,
            "classificacao": "maior",
            "origem": "materia_prima",
        },
        headers=headers,
    )
    assert resposta.status_code == 422


def test_abrir_rnc_tipo_cliente_sem_cliente_e_rejeitada(client, auth_headers, peca_pronta):
    headers = auth_headers(Perfil.OPERADOR)
    resposta = client.post(
        "/api/v1/nao-conformidades",
        json={
            "tipo": "cliente",
            "peca_id": peca_pronta["id"],
            "descricao_problema": "Devolução de cliente",
            "quantidade_afetada": 3,
            "classificacao": "maior",
            "origem": "processo",
        },
        headers=headers,
    )
    assert resposta.status_code == 422


def test_abrir_rnc_tipo_fornecedor_calcula_deteccao_interno(client, auth_headers, peca_pronta):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    fornecedor = client.post(
        "/api/v1/fornecedores", json={"codigo": "FORN-X", "nome": "Fornecedor X"}, headers=headers
    ).json()
    resposta = client.post(
        "/api/v1/nao-conformidades",
        json={
            "tipo": "fornecedor",
            "peca_id": peca_pronta["id"],
            "fornecedor_id": fornecedor["id"],
            "numero_nf_entrada": "NF-123",
            "descricao_problema": "Lote recebido fora de especificação",
            "quantidade_afetada": 5,
            "classificacao": "maior",
            "origem": "materia_prima",
            "deteccao": "cliente",  # deve ser ignorado e sobrescrito pelo backend
        },
        headers=headers,
    )
    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["deteccao"] == "interno"
    assert corpo["fornecedor"]["codigo"] == "FORN-X"


def test_abrir_rnc_tipo_cliente_calcula_deteccao_cliente(client, auth_headers, peca_pronta):
    headers = auth_headers(Perfil.OPERADOR)
    resposta = client.post(
        "/api/v1/nao-conformidades",
        json={
            "tipo": "cliente",
            "peca_id": peca_pronta["id"],
            "cliente": "Cliente Alfa",
            "vendedor": "Fulano",
            "numero_nf": "NF-999",
            "descricao_problema": "Devolução de cliente",
            "quantidade_afetada": 3,
            "classificacao": "maior",
            "origem": "processo",
        },
        headers=headers,
    )
    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["deteccao"] == "cliente"
    assert corpo["cliente"] == "Cliente Alfa"


def test_abrir_rnc_tipo_processo_com_operadores_maquina_setup(client, auth_headers, peca_pronta):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    maquina = client.post("/api/v1/maquinas", json={"codigo": "MAQ-X", "descricao": "Torno X"}, headers=headers).json()
    operador_id = client.get("/api/v1/usuarios", headers=headers).json()[0]["id"]

    resposta = client.post(
        "/api/v1/nao-conformidades",
        json={
            "tipo": "processo",
            "peca_id": peca_pronta["id"],
            "maquina_id": maquina["id"],
            "operadores_ids": [operador_id],
            "setup": True,
            "deteccao": "interno",
            "descricao_problema": "Problema no processo",
            "quantidade_afetada": 1,
            "classificacao": "menor",
            "origem": "processo",
        },
        headers=headers,
    )
    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["setup"] is True
    assert corpo["deteccao"] == "interno"
    assert corpo["maquina"]["codigo"] == "MAQ-X"
    assert len(corpo["operadores"]) == 1
    assert corpo["operadores"][0]["id"] == operador_id


def test_upload_e_download_de_foto(client, auth_headers, peca_pronta):
    headers = auth_headers(Perfil.OPERADOR)
    nc = client.post(
        "/api/v1/nao-conformidades",
        json={
            "peca_id": peca_pronta["id"],
            "descricao_problema": "Problema",
            "quantidade_afetada": 1,
            "classificacao": "menor",
            "origem": "processo",
        },
        headers=headers,
    ).json()

    conteudo_fake_png = b"\x89PNG\r\n\x1a\n" + b"0" * 100
    resposta = client.post(
        f"/api/v1/nao-conformidades/{nc['id']}/fotos",
        files=[("arquivos", ("defeito.png", conteudo_fake_png, "image/png"))],
        headers=headers,
    )
    assert resposta.status_code == 201, resposta.text
    foto = resposta.json()[0]
    assert foto["nome_arquivo"] == "defeito.png"
    assert foto["tamanho_bytes"] == len(conteudo_fake_png)

    resposta = client.get(f"/api/v1/nao-conformidades/{nc['id']}/fotos/{foto['id']}", headers=headers)
    assert resposta.status_code == 200
    assert resposta.content == conteudo_fake_png
    assert resposta.headers["content-type"] == "image/png"


def test_upload_foto_formato_nao_permitido_e_rejeitado(client, auth_headers, peca_pronta):
    headers = auth_headers(Perfil.OPERADOR)
    nc = client.post(
        "/api/v1/nao-conformidades",
        json={
            "peca_id": peca_pronta["id"],
            "descricao_problema": "Problema",
            "quantidade_afetada": 1,
            "classificacao": "menor",
            "origem": "processo",
        },
        headers=headers,
    ).json()

    resposta = client.post(
        f"/api/v1/nao-conformidades/{nc['id']}/fotos",
        files=[("arquivos", ("laudo.pdf", b"%PDF-1.4 fake", "application/pdf"))],
        headers=headers,
    )
    assert resposta.status_code == 400
    assert resposta.json()["code"] == "FOTO_FORMATO_INVALIDO"


def test_upload_foto_tamanho_excedido_e_rejeitado(client, auth_headers, peca_pronta):
    headers = auth_headers(Perfil.OPERADOR)
    nc = client.post(
        "/api/v1/nao-conformidades",
        json={
            "peca_id": peca_pronta["id"],
            "descricao_problema": "Problema",
            "quantidade_afetada": 1,
            "classificacao": "menor",
            "origem": "processo",
        },
        headers=headers,
    ).json()

    conteudo_grande = b"0" * (5 * 1024 * 1024 + 1)
    resposta = client.post(
        f"/api/v1/nao-conformidades/{nc['id']}/fotos",
        files=[("arquivos", ("grande.png", conteudo_grande, "image/png"))],
        headers=headers,
    )
    assert resposta.status_code == 400
    assert resposta.json()["code"] == "FOTO_TAMANHO_EXCEDIDO"


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
