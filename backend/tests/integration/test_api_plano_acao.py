from datetime import date, timedelta

import pytest

from app.core.permissions import Perfil


@pytest.fixture
def plano_novo(client, auth_headers):
    headers_op = auth_headers(Perfil.OPERADOR)
    headers_qual = auth_headers(Perfil.ANALISTA_QUALIDADE)

    peca = client.post(
        "/api/v1/pecas", json={"codigo": "PA-001", "descricao": "Peça plano", "revisao": "Rev. A"}, headers=headers_qual
    ).json()
    nc = client.post(
        "/api/v1/nao-conformidades",
        json={
            "peca_id": peca["id"],
            "descricao_problema": "Problema recorrente",
            "quantidade_afetada": 5,
            "classificacao": "critica",
            "origem": "processo",
        },
        headers=headers_op,
    ).json()
    nc = client.patch(
        f"/api/v1/nao-conformidades/{nc['id']}/tratamento",
        json={"disposicao": "retrabalho", "necessita_plano_acao": True},
        headers=headers_qual,
    ).json()
    responsavel_id = client.get("/api/v1/usuarios", headers=headers_qual).json()[0]["id"]
    return {"plano_id": nc["plano_acao_ativo_id"], "responsavel_id": responsavel_id, "headers_qual": headers_qual}


def test_plano_criado_automaticamente_com_status_aberto(client, plano_novo):
    resposta = client.get(f"/api/v1/planos-acao/{plano_novo['plano_id']}", headers=plano_novo["headers_qual"])
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "aberto"
    assert resposta.json()["acoes_corretivas"] == []


def test_adicionar_acao_transiciona_para_em_andamento(client, plano_novo):
    headers = plano_novo["headers_qual"]
    resposta = client.post(
        f"/api/v1/planos-acao/{plano_novo['plano_id']}/acoes",
        json={
            "descricao": "Revisar processo",
            "responsavel_id": plano_novo["responsavel_id"],
            "prazo": str(date.today() + timedelta(days=10)),
        },
        headers=headers,
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "em_andamento"
    assert len(corpo["acoes_corretivas"]) == 1
    assert corpo["acoes_corretivas"][0]["status"] == "pendente"


def test_avancar_verificacao_bloqueado_com_acao_pendente(client, plano_novo):
    headers = plano_novo["headers_qual"]
    client.post(
        f"/api/v1/planos-acao/{plano_novo['plano_id']}/acoes",
        json={
            "descricao": "Ação 1",
            "responsavel_id": plano_novo["responsavel_id"],
            "prazo": str(date.today() + timedelta(days=10)),
        },
        headers=headers,
    )
    resposta = client.post(f"/api/v1/planos-acao/{plano_novo['plano_id']}/avancar-verificacao", headers=headers)
    assert resposta.status_code == 400


def test_ciclo_completo_ate_encerramento_eficaz(client, plano_novo):
    headers = plano_novo["headers_qual"]
    plano_id = plano_novo["plano_id"]

    acao = client.post(
        f"/api/v1/planos-acao/{plano_id}/acoes",
        json={
            "descricao": "Ação 1",
            "responsavel_id": plano_novo["responsavel_id"],
            "prazo": str(date.today() + timedelta(days=10)),
        },
        headers=headers,
    ).json()["acoes_corretivas"][0]

    corpo = client.patch(f"/api/v1/planos-acao/{plano_id}/acoes/{acao['id']}/concluir", headers=headers).json()
    assert corpo["acoes_corretivas"][0]["status"] == "concluida"

    corpo = client.post(f"/api/v1/planos-acao/{plano_id}/avancar-verificacao", headers=headers).json()
    assert corpo["status"] == "aguardando_verificacao"

    corpo = client.post(
        f"/api/v1/planos-acao/{plano_id}/verificacao",
        json={
            "data_verificacao": str(date.today()),
            "responsavel_id": plano_novo["responsavel_id"],
            "resultado": "eficaz",
        },
        headers=headers,
    ).json()
    assert corpo["status"] == "encerrado"

    # não é possível adicionar ação em plano encerrado
    resposta = client.post(
        f"/api/v1/planos-acao/{plano_id}/acoes",
        json={
            "descricao": "Ação extra",
            "responsavel_id": plano_novo["responsavel_id"],
            "prazo": str(date.today()),
        },
        headers=headers,
    )
    assert resposta.status_code == 400


def test_verificacao_nao_eficaz_reabre_e_incrementa_ciclo(client, plano_novo):
    headers = plano_novo["headers_qual"]
    plano_id = plano_novo["plano_id"]

    acao1 = client.post(
        f"/api/v1/planos-acao/{plano_id}/acoes",
        json={
            "descricao": "Ação 1",
            "responsavel_id": plano_novo["responsavel_id"],
            "prazo": str(date.today() + timedelta(days=10)),
        },
        headers=headers,
    ).json()["acoes_corretivas"][0]
    client.patch(f"/api/v1/planos-acao/{plano_id}/acoes/{acao1['id']}/concluir", headers=headers)
    client.post(f"/api/v1/planos-acao/{plano_id}/avancar-verificacao", headers=headers)

    corpo = client.post(
        f"/api/v1/planos-acao/{plano_id}/verificacao",
        json={
            "data_verificacao": str(date.today()),
            "responsavel_id": plano_novo["responsavel_id"],
            "resultado": "nao_eficaz",
        },
        headers=headers,
    ).json()
    assert corpo["status"] == "reaberto"
    assert corpo["ciclo"] == 2
    # ação do ciclo 1 continua no histórico, visível na lista.
    assert len(corpo["acoes_corretivas"]) == 1

    # nova ação corretiva do 2º ciclo reabre o andamento do plano.
    corpo = client.post(
        f"/api/v1/planos-acao/{plano_id}/acoes",
        json={
            "descricao": "Ação 2 (novo ciclo)",
            "responsavel_id": plano_novo["responsavel_id"],
            "prazo": str(date.today() + timedelta(days=5)),
        },
        headers=headers,
    ).json()
    assert corpo["status"] == "em_andamento"
    assert len(corpo["acoes_corretivas"]) == 2
    assert corpo["acoes_corretivas"][1]["ciclo"] == 2


def test_ishikawa_marcar_raiz_atualiza_conclusao(client, plano_novo):
    headers = plano_novo["headers_qual"]
    plano_id = plano_novo["plano_id"]

    client.patch(f"/api/v1/planos-acao/{plano_id}/metodologia", json={"metodologia_causa_raiz": "ishikawa"}, headers=headers)
    corpo = client.post(
        f"/api/v1/planos-acao/{plano_id}/causas-ishikawa",
        json={"categoria": "maquina", "descricao_causa": "Máquina descalibrada"},
        headers=headers,
    ).json()
    causa_id = corpo["causas_ishikawa"][0]["id"]

    corpo = client.patch(
        f"/api/v1/planos-acao/{plano_id}/causas-ishikawa/{causa_id}/marcar-raiz",
        json={"marcada_como_raiz": True},
        headers=headers,
    ).json()
    assert corpo["conclusao_causa_raiz"] == "Máquina descalibrada"


def test_5porques_marcar_raiz_atualiza_conclusao(client, plano_novo):
    headers = plano_novo["headers_qual"]
    plano_id = plano_novo["plano_id"]

    client.patch(
        f"/api/v1/planos-acao/{plano_id}/metodologia", json={"metodologia_causa_raiz": "cinco_porques"}, headers=headers
    )
    corpo = client.put(
        f"/api/v1/planos-acao/{plano_id}/causas-5porques",
        json={"nivel": 1, "pergunta": "Por que falhou?", "resposta": "Falta de padronização"},
        headers=headers,
    ).json()
    causa_id = corpo["causas_5porques"][0]["id"]

    corpo = client.patch(
        f"/api/v1/planos-acao/{plano_id}/causas-5porques/{causa_id}/marcar-raiz",
        json={"marcada_como_raiz": True},
        headers=headers,
    ).json()
    assert corpo["conclusao_causa_raiz"] == "Falta de padronização"


def test_trocar_metodologia_limpa_conclusao_mas_preserva_causas(client, plano_novo):
    headers = plano_novo["headers_qual"]
    plano_id = plano_novo["plano_id"]

    client.patch(f"/api/v1/planos-acao/{plano_id}/metodologia", json={"metodologia_causa_raiz": "ishikawa"}, headers=headers)
    corpo = client.post(
        f"/api/v1/planos-acao/{plano_id}/causas-ishikawa",
        json={"categoria": "material", "descricao_causa": "Matéria-prima fora de especificação"},
        headers=headers,
    ).json()
    causa_id = corpo["causas_ishikawa"][0]["id"]
    client.patch(
        f"/api/v1/planos-acao/{plano_id}/causas-ishikawa/{causa_id}/marcar-raiz",
        json={"marcada_como_raiz": True},
        headers=headers,
    )

    corpo = client.patch(
        f"/api/v1/planos-acao/{plano_id}/metodologia", json={"metodologia_causa_raiz": "livre"}, headers=headers
    ).json()
    assert corpo["conclusao_causa_raiz"] is None
    # a causa continua salva no banco (histórico), mesmo não sendo mais a metodologia ativa.
    corpo_detalhe = client.get(f"/api/v1/planos-acao/{plano_id}", headers=headers).json()
    assert len(corpo_detalhe["causas_ishikawa"]) == 1
