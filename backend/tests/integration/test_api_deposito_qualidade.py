from app.core.permissions import Perfil

PECA_PAYLOAD = {"codigo": "PECA-DEP-001", "descricao": "Peça de teste", "revisao": "A"}


def _criar_peca(client, headers) -> dict:
    resposta = client.post("/api/v1/pecas", json=PECA_PAYLOAD, headers=headers)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def test_operador_nao_pode_criar_bloqueio(client, auth_headers):
    headers_gestor = auth_headers(Perfil.GESTOR_QUALIDADE)
    peca = _criar_peca(client, headers_gestor)

    headers_operador = auth_headers(Perfil.OPERADOR)
    resposta = client.post(
        "/api/v1/deposito-qualidade",
        json={"peca_id": peca["id"], "motivo": "Diâmetro fora de especificação"},
        headers=headers_operador,
    )
    assert resposta.status_code == 403


def test_inspetor_nao_pode_criar_mas_pode_consultar(client, auth_headers):
    headers_gestor = auth_headers(Perfil.GESTOR_QUALIDADE)
    peca = _criar_peca(client, headers_gestor)
    client.post(
        "/api/v1/deposito-qualidade",
        json={"peca_id": peca["id"], "motivo": "Diâmetro fora de especificação"},
        headers=headers_gestor,
    )

    headers_inspetor = auth_headers(Perfil.INSPETOR)
    resposta_criar = client.post(
        "/api/v1/deposito-qualidade",
        json={"peca_id": peca["id"], "motivo": "Outro motivo"},
        headers=headers_inspetor,
    )
    assert resposta_criar.status_code == 403

    resposta_buscar = client.get(
        "/api/v1/deposito-qualidade/buscar", params={"codigo_peca": peca["codigo"]}, headers=headers_inspetor
    )
    assert resposta_buscar.status_code == 200
    corpo = resposta_buscar.json()
    assert corpo["peca"]["codigo"] == peca["codigo"]
    assert len(corpo["bloqueios"]) == 1
    assert corpo["bloqueios"][0]["motivo"] == "Diâmetro fora de especificação"
    assert corpo["bloqueios"][0]["status"] == "bloqueado"


def test_analista_cria_multiplos_bloqueios_e_libera(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    peca = _criar_peca(client, headers)

    b1 = client.post(
        "/api/v1/deposito-qualidade",
        json={
            "peca_id": peca["id"],
            "motivo": "Entregue ao cliente X com diâmetro maior que o especificado",
            "caracteristica_atencao": "Diâmetro externo (posição 1 do desenho)",
            "cliente": "Cliente X",
        },
        headers=headers,
    ).json()
    b2 = client.post(
        "/api/v1/deposito-qualidade",
        json={"peca_id": peca["id"], "motivo": "Segundo motivo de bloqueio"},
        headers=headers,
    ).json()
    assert b1["id"] != b2["id"]

    busca = client.get(
        "/api/v1/deposito-qualidade/buscar", params={"codigo_peca": peca["codigo"]}, headers=headers
    ).json()
    assert len(busca["bloqueios"]) == 2

    resposta_liberar = client.patch(
        f"/api/v1/deposito-qualidade/{b1['id']}/liberar",
        json={"observacao_liberacao": "Retrabalho concluído, peça conforme"},
        headers=headers,
    )
    assert resposta_liberar.status_code == 200
    assert resposta_liberar.json()["status"] == "liberado"

    resposta_liberar_de_novo = client.patch(
        f"/api/v1/deposito-qualidade/{b1['id']}/liberar",
        json={"observacao_liberacao": "Tentando de novo"},
        headers=headers,
    )
    assert resposta_liberar_de_novo.status_code == 400
    assert resposta_liberar_de_novo.json()["code"] == "BLOQUEIO_JA_LIBERADO"


def test_buscar_por_codigo_inexistente_retorna_404(client, auth_headers):
    headers = auth_headers(Perfil.INSPETOR)
    resposta = client.get(
        "/api/v1/deposito-qualidade/buscar", params={"codigo_peca": "NAO-EXISTE"}, headers=headers
    )
    assert resposta.status_code == 404


def test_upload_e_download_de_foto(client, auth_headers):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    peca = _criar_peca(client, headers)
    bloqueio = client.post(
        "/api/v1/deposito-qualidade",
        json={"peca_id": peca["id"], "motivo": "Motivo qualquer"},
        headers=headers,
    ).json()
    assert bloqueio["tem_foto"] is False

    arquivo = (b"\xff\xd8\xff\xdb" + b"0" * 100, "foto.jpg", "image/jpeg")
    resposta_upload = client.post(
        f"/api/v1/deposito-qualidade/{bloqueio['id']}/foto",
        files={"arquivo": (arquivo[1], arquivo[0], arquivo[2])},
        headers=headers,
    )
    assert resposta_upload.status_code == 200
    assert resposta_upload.json()["tem_foto"] is True

    resposta_foto = client.get(f"/api/v1/deposito-qualidade/{bloqueio['id']}/foto", headers=headers)
    assert resposta_foto.status_code == 200
    assert resposta_foto.headers["content-type"] == "image/jpeg"


def test_upload_foto_formato_invalido_e_rejeitado(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    peca = _criar_peca(client, headers)
    bloqueio = client.post(
        "/api/v1/deposito-qualidade",
        json={"peca_id": peca["id"], "motivo": "Motivo qualquer"},
        headers=headers,
    ).json()

    resposta = client.post(
        f"/api/v1/deposito-qualidade/{bloqueio['id']}/foto",
        files={"arquivo": ("arquivo.txt", b"conteudo", "text/plain")},
        headers=headers,
    )
    assert resposta.status_code == 400
    assert resposta.json()["code"] == "FOTO_FORMATO_INVALIDO"
