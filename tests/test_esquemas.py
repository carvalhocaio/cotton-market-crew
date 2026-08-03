import pytest
from pydantic import ValidationError

from cotton_market_crew.esquemas import (
    AnaliseConsolidada,
    AnaliseFisico,
    AnaliseMercadoExterno,
)


class TestAnaliseFisico:
    def test_cria_analise_valida(self):
        analise = AnaliseFisico(
            regiao="MT",
            tendencia="alta",
            basis_cents_lb=18.37,
            comentario="Basis positivo puxado por demanda firme na região.",
        )

        assert analise.regiao == "MT"
        assert analise.tendencia == "alta"
        assert analise.basis_cents_lb == 18.37

    def test_rejeita_regiao_fora_do_dominio(self):
        with pytest.raises(ValidationError):
            AnaliseFisico(
                regiao="SP",
                tendencia="alta",
                basis_cents_lb=18.37,
                comentario="Basis positivo puxado por demanda firme na região.",
            )

    def test_rejeita_tendencia_fora_do_dominio(self):
        with pytest.raises(ValidationError):
            AnaliseFisico(
                regiao="MT",
                tendencia="explosiva",
                basis_cents_lb=18.37,
                comentario="Basis positivo puxado por demanda firme na região.",
            )

    def test_rejeita_comentario_curto_demais(self):
        with pytest.raises(ValidationError):
            AnaliseFisico(
                regiao="MT",
                tendencia="alta",
                basis_cents_lb=18.37,
                comentario="ok",
            )

    def test_rejeita_campo_extra_nao_declarado(self):
        with pytest.raises(ValidationError):
            AnaliseFisico(
                regiao="MT",
                tendencia="alta",
                basis_cents_lb=18.37,
                comentario="Basis positivo puxado por demanda firme na região.",
                confianca=0.9,
            )

    def test_rejeita_basis_com_tipo_invalido(self):
        with pytest.raises(ValidationError):
            AnaliseFisico(
                regiao="MT",
                tendencia="alta",
                basis_cents_lb="dezoito",
                comentario="Basis positivo puxado por demanda firme na região.",
            )


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


class TestAnaliseMercadoExterno:
    def test_cria_analise_valida(self):
        analise = AnaliseMercadoExterno(
            tendencia_futuro="alta",
            pressao_cambial="favoravel",
            comentario=(
                "Contrato futuro em alta e câmbio depreciado favorecem a "
                "competitividade do algodão brasileiro no curto prazo."
            ),
        )

        assert analise.tendencia_futuro == "alta"
        assert analise.pressao_cambial == "favoravel"

    def test_rejeita_tendencia_fora_do_dominio(self):
        with pytest.raises(ValidationError):
            AnaliseMercadoExterno(
                tendencia_futuro="explosiva",
                pressao_cambial="favoravel",
                comentario=(
                    "Contrato futuro em alta e câmbio depreciado favorecem "
                    "a competitividade do algodão brasileiro."
                ),
            )

    def test_rejeita_pressao_cambial_fora_do_dominio(self):
        with pytest.raises(ValidationError):
            AnaliseMercadoExterno(
                tendencia_futuro="alta",
                pressao_cambial="neutra-ish",
                comentario=(
                    "Contrato futuro em alta e câmbio depreciado favorecem "
                    "a competitividade do algodão brasileiro."
                ),
            )

    def test_rejeita_comentario_curto_demais(self):
        with pytest.raises(ValidationError):
            AnaliseMercadoExterno(
                tendencia_futuro="alta",
                pressao_cambial="favoravel",
                comentario="Alta.",
            )

    def test_rejeita_campo_extra_nao_declarado(self):
        with pytest.raises(ValidationError):
            AnaliseMercadoExterno(
                tendencia_futuro="alta",
                pressao_cambial="favoravel",
                comentario=(
                    "Contrato futuro em alta e câmbio depreciado favorecem "
                    "a competitividade do algodão brasileiro."
                ),
                fonte="ICE",
            )
