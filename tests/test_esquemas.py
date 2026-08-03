# tests/test_esquemas.py
import pytest
from pydantic import ValidationError

from cotton_market_crew.esquemas import AnaliseFisico


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
