from datetime import date
from decimal import Decimal

import pytest
from cotton_market_crew.dominio import (
    Basis,
    BasisInvalidoError,
    Cambio,
    CotacaoFutura,
    CotacaoInvalidaError,
    IndicadorFisico,
    IndicadorInvalidoError,
)


class TestIndicadorFisico:
    def test_cria_indicador_valido(self):
        indicador = IndicadorFisico(
            data=date(2026, 7, 27),
            regiao="MT",
            reais_por_arroba=Decimal("158.50"),
        )

        assert indicador.regiao == "MT"
        assert indicador.reais_por_arroba == Decimal("158.50")
        assert indicador.fonte == "CEPEA/ESALQ"

    def test_indicador_e_imutavel(self):
        indicador = IndicadorFisico(
            data=date(2026, 7, 27),
            regiao="MT",
            reais_por_arroba=Decimal("158.50"),
        )

        with pytest.raises(AttributeError):
            indicador.reais_por_arroba = Decimal("999")

    def test_rejeita_valor_nao_positivo(self):
        with pytest.raises(IndicadorInvalidoError):
            IndicadorFisico(
                data=date(2026, 7, 27),
                regiao="SP",
                reais_por_arroba=Decimal("158.50"),
            )


class TestCotacaoFutura:
    def test_cria_cotacao_valida(self):
        cotacao = CotacaoFutura(
            data=date(2026, 7, 27),
            contrato="DEZ26",
            cents_por_libra=Decimal("71.35"),
        )

        assert cotacao.contrato == "DEZ26"
        assert cotacao.fonte == "ICE Futures US #2"

    def test_rejeita_cotacao_nao_positiva(self):
        with pytest.raises(CotacaoInvalidaError):
            CotacaoFutura(
                data=date(2026, 7, 27),
                contrato="DEZ26",
                cents_por_libra=Decimal("-1"),
            )


class TestCambio:
    def test_cria_cambio_valido(self):
        cambio = Cambio(data=date(2026, 7, 27), ptax_venda=Decimal("5.3421"))

        assert cambio.ptax_venda == Decimal("5.3421")

    def test_rejeita_ptax_nao_positivo(self):
        with pytest.raises(CotacaoInvalidaError):
            Cambio(data=date(2026, 7, 27), ptax_venda=Decimal("0"))


class TestBasis:
    def test_cria_basis_valido(self):
        basis = Basis(
            data=date(2026, 7, 27),
            regiao="MT",
            valor_cents_por_libra=Decimal("-3.20"),
        )

        assert basis.regiao == "MT"
        assert basis.valor_cents_por_libra == Decimal("-3.20")

    def test_rejeita_regiao_desconhecida(self):
        with pytest.raises(BasisInvalidoError):
            Basis(
                data=date(2026, 7, 27),
                regiao="SP",
                valor_cents_por_libra=Decimal("-3.20"),
            )
