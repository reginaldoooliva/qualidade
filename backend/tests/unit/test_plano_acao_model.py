from datetime import date, timedelta

from app.models.plano_acao import AcaoCorretiva, StatusAcaoCorretiva


def test_acao_pendente_com_prazo_futuro_nao_esta_atrasada():
    acao = AcaoCorretiva(prazo=date.today() + timedelta(days=5), status=StatusAcaoCorretiva.PENDENTE)
    assert acao.status_calculado == "pendente"


def test_acao_pendente_com_prazo_vencido_esta_atrasada():
    acao = AcaoCorretiva(prazo=date.today() - timedelta(days=1), status=StatusAcaoCorretiva.PENDENTE)
    assert acao.status_calculado == "atrasada"


def test_acao_concluida_nunca_esta_atrasada_mesmo_com_prazo_vencido():
    acao = AcaoCorretiva(prazo=date.today() - timedelta(days=1), status=StatusAcaoCorretiva.CONCLUIDA)
    assert acao.status_calculado == "concluida"
