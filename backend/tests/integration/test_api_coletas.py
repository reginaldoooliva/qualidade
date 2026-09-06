import pytest

from app.core.permissions import Perfil


@pytest.fixture
def setup_peca_etapa(client, auth_headers):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    peca = client.post(
        "/api/v1/pecas", json={"codigo": "COL-001", "descricao": "Peça coleta", "revisao": "Rev. A"}, headers=headers
    ).json()
    etapa = client.post(
        f"/api/v1/pecas/{peca['id']}/etapas",
        json={"numero_etapa": 10, "freq_numerador": 1, "freq_denominador": 1},
        headers=headers,
    ).json()
    caracteristica = client.post(
        f"/api/v1/etapas/{etapa['id']}/caracteristicas",
        json={"nome": "Diâmetro", "nominal": 10.0, "tol_superior": 0.1, "tol_inferior": 0.1, "unidade": "mm"},
        headers=headers,
    ).json()
    return {"peca": peca, "etapa": etapa, "caracteristica": caracteristica}


def test_iniciar_coleta_nova_ordem_exige_quantidade(client, auth_headers, setup_peca_etapa):
    headers = auth_headers(Perfil.OPERADOR)
    resposta = client.post(
        "/api/v1/coletas/iniciar",
        json={"peca_id": setup_peca_etapa["peca"]["id"], "numero_ordem": "OP-1", "etapa_id": setup_peca_etapa["etapa"]["id"]},
        headers=headers,
    )
    assert resposta.status_code == 400
    assert resposta.json()["code"] == "QUANTIDADE_ORDEM_OBRIGATORIA"


def test_iniciar_coleta_calcula_amostras(client, auth_headers, setup_peca_etapa):
    headers = auth_headers(Perfil.OPERADOR)
    resposta = client.post(
        "/api/v1/coletas/iniciar",
        json={
            "peca_id": setup_peca_etapa["peca"]["id"],
            "numero_ordem": "OP-2",
            "quantidade_ordem": 2,
            "etapa_id": setup_peca_etapa["etapa"]["id"],
        },
        headers=headers,
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["amostras_calculadas"] == 2
    assert corpo["amostras_alvo"] == 2
    assert corpo["status"] == "em_andamento"
    assert len(corpo["caracteristicas"]) == 1


def test_iniciar_coleta_continuidade_rodada_em_andamento(client, auth_headers, setup_peca_etapa):
    headers = auth_headers(Perfil.OPERADOR)
    payload = {
        "peca_id": setup_peca_etapa["peca"]["id"],
        "numero_ordem": "OP-3",
        "quantidade_ordem": 5,
        "etapa_id": setup_peca_etapa["etapa"]["id"],
    }
    r1 = client.post("/api/v1/coletas/iniciar", json=payload, headers=headers).json()
    r2 = client.post("/api/v1/coletas/iniciar", json={**payload, "quantidade_ordem": None}, headers=headers).json()
    assert r1["id"] == r2["id"]


def test_salvar_medicao_e_finalizar_completo(client, auth_headers, setup_peca_etapa):
    headers = auth_headers(Perfil.OPERADOR)
    rodada = client.post(
        "/api/v1/coletas/iniciar",
        json={
            "peca_id": setup_peca_etapa["peca"]["id"],
            "numero_ordem": "OP-4",
            "quantidade_ordem": 2,
            "etapa_id": setup_peca_etapa["etapa"]["id"],
        },
        headers=headers,
    ).json()
    caracteristica_id = setup_peca_etapa["caracteristica"]["id"]

    m1 = client.put(
        f"/api/v1/coletas/{rodada['id']}/medicoes/{caracteristica_id}/1", json={"valor": 10.02}, headers=headers
    )
    assert m1.status_code == 200
    assert m1.json()["operador_nome"]

    client.put(f"/api/v1/coletas/{rodada['id']}/medicoes/{caracteristica_id}/2", json={"valor": 9.99}, headers=headers)

    detalhe = client.get(f"/api/v1/coletas/{rodada['id']}", headers=headers).json()
    assert len(detalhe["medicoes"]) == 2

    finalizar = client.post(f"/api/v1/coletas/{rodada['id']}/finalizar", json={}, headers=headers)
    assert finalizar.status_code == 200
    assert finalizar.json()["status"] == "finalizada"
    assert finalizar.json()["sugestao_abrir_rnc"] is False


def test_finalizar_incompleto_exige_motivo(client, auth_headers, setup_peca_etapa):
    headers = auth_headers(Perfil.OPERADOR)
    rodada = client.post(
        "/api/v1/coletas/iniciar",
        json={
            "peca_id": setup_peca_etapa["peca"]["id"],
            "numero_ordem": "OP-5",
            "quantidade_ordem": 2,
            "etapa_id": setup_peca_etapa["etapa"]["id"],
        },
        headers=headers,
    ).json()

    sem_motivo = client.post(f"/api/v1/coletas/{rodada['id']}/finalizar", json={}, headers=headers)
    assert sem_motivo.status_code == 400
    assert sem_motivo.json()["code"] == "MOTIVO_ENCERRAMENTO_OBRIGATORIO"

    com_motivo = client.post(
        f"/api/v1/coletas/{rodada['id']}/finalizar",
        json={"motivo_encerramento_antecipado": "ordem_cancelada"},
        headers=headers,
    )
    assert com_motivo.status_code == 200
    assert com_motivo.json()["status"] == "finalizada_com_pendencia"


def test_medicao_fora_de_especificacao_sugere_rnc(client, auth_headers, setup_peca_etapa):
    headers = auth_headers(Perfil.OPERADOR)
    rodada = client.post(
        "/api/v1/coletas/iniciar",
        json={
            "peca_id": setup_peca_etapa["peca"]["id"],
            "numero_ordem": "OP-6",
            "quantidade_ordem": 1,
            "etapa_id": setup_peca_etapa["etapa"]["id"],
        },
        headers=headers,
    ).json()
    caracteristica_id = setup_peca_etapa["caracteristica"]["id"]
    # nominal 10, tol +-0.1 -> LSE=10.1, LIE=9.9 — 11.0 está fora de especificação
    client.put(f"/api/v1/coletas/{rodada['id']}/medicoes/{caracteristica_id}/1", json={"valor": 11.0}, headers=headers)

    finalizar = client.post(f"/api/v1/coletas/{rodada['id']}/finalizar", json={}, headers=headers)
    assert finalizar.status_code == 200
    assert finalizar.json()["sugestao_abrir_rnc"] is True


def test_nao_permite_nova_rodada_quando_ja_finalizada(client, auth_headers, setup_peca_etapa):
    headers = auth_headers(Perfil.OPERADOR)
    payload = {
        "peca_id": setup_peca_etapa["peca"]["id"],
        "numero_ordem": "OP-7",
        "quantidade_ordem": 1,
        "etapa_id": setup_peca_etapa["etapa"]["id"],
    }
    rodada = client.post("/api/v1/coletas/iniciar", json=payload, headers=headers).json()
    client.post(
        f"/api/v1/coletas/{rodada['id']}/finalizar",
        json={"motivo_encerramento_antecipado": "ordem_cancelada"},
        headers=headers,
    )

    segunda_tentativa = client.post("/api/v1/coletas/iniciar", json={**payload, "quantidade_ordem": None}, headers=headers)
    assert segunda_tentativa.status_code == 409
    assert segunda_tentativa.json()["code"] == "RODADA_JA_FINALIZADA"


def test_reabrir_requer_perfil_qualidade(client, auth_headers, setup_peca_etapa):
    headers_operador = auth_headers(Perfil.OPERADOR)
    payload = {
        "peca_id": setup_peca_etapa["peca"]["id"],
        "numero_ordem": "OP-8",
        "quantidade_ordem": 1,
        "etapa_id": setup_peca_etapa["etapa"]["id"],
    }
    rodada = client.post("/api/v1/coletas/iniciar", json=payload, headers=headers_operador).json()
    client.post(
        f"/api/v1/coletas/{rodada['id']}/finalizar",
        json={"motivo_encerramento_antecipado": "ordem_cancelada"},
        headers=headers_operador,
    )

    tentativa_operador = client.post(f"/api/v1/coletas/{rodada['id']}/reabrir", headers=headers_operador)
    assert tentativa_operador.status_code == 403

    headers_analista = auth_headers(Perfil.ANALISTA_QUALIDADE)
    tentativa_analista = client.post(f"/api/v1/coletas/{rodada['id']}/reabrir", headers=headers_analista)
    assert tentativa_analista.status_code == 200
    assert tentativa_analista.json()["status"] == "em_andamento"


def test_excluir_medicao(client, auth_headers, setup_peca_etapa):
    headers = auth_headers(Perfil.OPERADOR)
    rodada = client.post(
        "/api/v1/coletas/iniciar",
        json={
            "peca_id": setup_peca_etapa["peca"]["id"],
            "numero_ordem": "OP-9",
            "quantidade_ordem": 1,
            "etapa_id": setup_peca_etapa["etapa"]["id"],
        },
        headers=headers,
    ).json()
    caracteristica_id = setup_peca_etapa["caracteristica"]["id"]
    client.put(f"/api/v1/coletas/{rodada['id']}/medicoes/{caracteristica_id}/1", json={"valor": 10.0}, headers=headers)

    excluir = client.delete(f"/api/v1/coletas/{rodada['id']}/medicoes/{caracteristica_id}/1", headers=headers)
    assert excluir.status_code == 204

    detalhe = client.get(f"/api/v1/coletas/{rodada['id']}", headers=headers).json()
    assert len(detalhe["medicoes"]) == 0


def test_ordem_existente_e_reaproveitada(client, auth_headers, setup_peca_etapa):
    headers = auth_headers(Perfil.ANALISTA_QUALIDADE)
    peca_id = setup_peca_etapa["peca"]["id"]

    etapa2 = client.post(
        f"/api/v1/pecas/{peca_id}/etapas",
        json={"numero_etapa": 20, "freq_numerador": 1, "freq_denominador": 1},
        headers=headers,
    ).json()

    client.post(
        "/api/v1/coletas/iniciar",
        json={
            "peca_id": peca_id,
            "numero_ordem": "OP-10",
            "quantidade_ordem": 7,
            "etapa_id": setup_peca_etapa["etapa"]["id"],
        },
        headers=headers,
    )

    resposta = client.get(f"/api/v1/pecas/{peca_id}/ordens/OP-10", headers=headers)
    assert resposta.status_code == 200
    assert resposta.json()["quantidade"] == 7

    rodada_etapa2 = client.post(
        "/api/v1/coletas/iniciar",
        json={"peca_id": peca_id, "numero_ordem": "OP-10", "etapa_id": etapa2["id"]},
        headers=headers,
    )
    assert rodada_etapa2.status_code == 200
    assert rodada_etapa2.json()["amostras_calculadas"] == 7
