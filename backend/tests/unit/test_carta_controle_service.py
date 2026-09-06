import pytest

from app.services.carta_controle_service import _constantes, _montar_subgrupos


class _RodadaFake:
    def __init__(self, id, numero_ordem, data_hora_inicio):
        self.id = id
        self.numero_ordem = numero_ordem
        self.data_hora_inicio = data_hora_inicio


@pytest.mark.parametrize(
    "n_medio,esperado",
    [
        (2, (1.880, 0.000, 3.267)),
        (3, (1.023, 0.000, 2.574)),
        (5, (0.577, 0.000, 2.114)),
        (1, (1.880, 0.000, 3.267)),  # abaixo do mínimo suportado -> usa n=2
        (2.4, (1.880, 0.000, 3.267)),  # arredonda para 2
        (2.6, (1.023, 0.000, 2.574)),  # arredonda para 3
        (25, (0.308, 0.223, 1.777)),  # acima do máximo suportado -> usa n=10
    ],
)
def test_constantes_controle(n_medio, esperado):
    assert _constantes(n_medio) == esperado


def test_montar_subgrupos_ignora_rodadas_com_menos_de_duas_medicoes():
    rodadas = [_RodadaFake(1, "OP-1", "2026-01-01"), _RodadaFake(2, "OP-2", "2026-01-02")]
    valores_por_rodada = {1: [10.0], 2: [11.0, 12.0, 13.0]}

    subgrupos = _montar_subgrupos(rodadas, valores_por_rodada)

    assert len(subgrupos) == 1
    assert subgrupos[0]["rodada_id"] == 2
    assert subgrupos[0]["n"] == 3
    assert subgrupos[0]["media"] == pytest.approx(12.0)
    assert subgrupos[0]["amplitude"] == pytest.approx(2.0)


def test_montar_subgrupos_calcula_media_e_amplitude():
    rodadas = [_RodadaFake(1, "OP-1", "2026-01-01")]
    valores_por_rodada = {1: [10.0, 12.0, 14.0]}

    subgrupos = _montar_subgrupos(rodadas, valores_por_rodada)

    assert subgrupos[0]["media"] == pytest.approx(12.0)
    assert subgrupos[0]["amplitude"] == pytest.approx(4.0)
