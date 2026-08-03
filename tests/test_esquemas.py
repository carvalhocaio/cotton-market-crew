import pytest
from pydantic import ValidationError

from cotton_market_crew.esquemas import AnaliseConsolidada


class TestAnaliseConsolidada:
    def test_cria_analise_consolidada_valida(self):
        analise = AnaliseConsolidada(
            tendencia_geral="alta",
            regiao_destaque="MT",
            basis_medio_cents_lb=15.20,
            comentario_estrategico=(
                "Basis firme nas três praças reforça viés de alta para o "
                "físico no curto prazo, com destaque para Mato Grosso."
            ),
        )

        assert analise.tendencia_geral == "alta"
        assert analise.regiao_destaque == "MT"

    def test_rejeita_tendencia_fora_do_dominio(self):
        with pytest.raises(ValidationError):
            AnaliseConsolidada(
                tendencia_geral="explosiva",
                regiao_destaque="MT",
                basis_medio_cents_lb=15.20,
                comentario_estrategico=(
                    "Basis firme nas três praças reforça viés de alta para "
                    "o físico no curto prazo."
                ),
            )

    def test_rejeita_regiao_destaque_fora_do_dominio(self):
        with pytest.raises(ValidationError):
            AnaliseConsolidada(
                tendencia_geral="alta",
                regiao_destaque="SP",
                basis_medio_cents_lb=15.20,
                comentario_estrategico=(
                    "Basis firme nas três praças reforça viés de alta para "
                    "o físico no curto prazo."
                ),
            )

    def test_rejeita_comentario_curto_demais(self):
        with pytest.raises(ValidationError):
            AnaliseConsolidada(
                tendencia_geral="alta",
                regiao_destaque="MT",
                basis_medio_cents_lb=15.20,
                comentario_estrategico="Alta.",
            )

    def test_rejeita_campo_extra_nao_declarado(self):
        with pytest.raises(ValidationError):
            AnaliseConsolidada(
                tendencia_geral="alta",
                regiao_destaque="MT",
                basis_medio_cents_lb=15.20,
                comentario_estrategico=(
                    "Basis firme nas três praças reforça viés de alta para "
                    "o físico no curto prazo."
                ),
                recomendacao="comprar",
            )
