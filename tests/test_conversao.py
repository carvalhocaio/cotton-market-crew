from decimal import Decimal

import pytest

from cotton_market_crew.conversao import (
    ConversaoInvalidaError,
    arroba_reais_para_cents_libra,
)


class TestArrobaReaisParaCentsLibra:
    def test_converte_valor_conhecido(self):
        resultado = arroba_reais_para_cents_libra(
            reais_por_arroba=Decimal("158.50"),
            ptax_venda=Decimal("5.3421"),
        )

        assert resultado == Decimal("89.72")

    def test_ptax_maior_resulta_em_cents_menor(self):
        base = arroba_reais_para_cents_libra(
            reais_por_arroba=Decimal("158.50"),
            ptax_venda=Decimal("5.00"),
        )
        com_ptax_maior = arroba_reais_para_cents_libra(
            reais_por_arroba=Decimal("158.50"),
            ptax_venda=Decimal("5.50"),
        )

        assert com_ptax_maior < base

    def test_rejeita_reais_por_arroba_nao_positivo(self):
        with pytest.raises(ConversaoInvalidaError):
            arroba_reais_para_cents_libra(
                reais_por_arroba=Decimal("0"),
                ptax_venda=Decimal("5.34"),
            )

    def test_rejeita_ptax_nao_positivo(self):
        with pytest.raises(ConversaoInvalidaError):
            arroba_reais_para_cents_libra(
                reais_por_arroba=Decimal("158.50"),
                ptax_venda=Decimal("0"),
            )
