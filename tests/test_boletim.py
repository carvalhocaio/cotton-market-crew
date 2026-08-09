from datetime import date

from cotton_market_crew.boletim import DISCLAIMER_PADRAO, renderizar_boletim
from cotton_market_crew.esquemas import AnaliseConsolidada


def _consolidada() -> AnaliseConsolidada:
    return AnaliseConsolidada(
        tendencia_geral="alta",
        regiao_destaque="GO",
        basis_medio_cents_lb=13.36,
        comentario_estrategico=(
            "O mercado físico regional demonstra forte tendência de alta, "
            "com basis elevados em MT, BA e GO."
        ),
    )


class TestRenderizarBoletim:
    def test_contem_titulo(self):
        boletim = renderizar_boletim(_consolidada(), data_base=date(2026, 7, 24))

        assert "Boletim de Mercado de Algodão" in boletim

    def test_contem_data_base_formatada(self):
        boletim = renderizar_boletim(_consolidada(), data_base=date(2026, 7, 24))

        assert "24/07/2026" in boletim

    def test_contem_tendencia_e_regiao_destaque(self):
        boletim = renderizar_boletim(_consolidada(), data_base=date(2026, 7, 24))

        assert "alta" in boletim.lower()
        assert "GO" in boletim

    def test_contem_basis_medio_formatado(self):
        boletim = renderizar_boletim(_consolidada(), data_base=date(2026, 7, 24))

        assert "13.36" in boletim

    def test_contem_comentario_estrategico_completo(self):
        consolidada = _consolidada()
        boletim = renderizar_boletim(consolidada, data_base=date(2026, 7, 24))

        assert consolidada.comentario_estrategico in boletim

    def test_sempre_contem_o_disclaimer_padrao(self):
        boletim = renderizar_boletim(_consolidada(), data_base=date(2026, 7, 24))

        assert DISCLAIMER_PADRAO in boletim

    def test_disclaimer_e_identico_independente_do_conteudo(self):
        """O disclaimer nunca passa pelo LLM - é texto fixo, sempre igual."""
        consolidada_2 = AnaliseConsolidada(
            tendencia_geral="queda",
            regiao_destaque="BA",
            basis_medio_cents_lb=-5.0,
            comentario_estrategico=(
                "Comentário completamente diferente do outro caso de teste."
            ),
        )

        boletim_1 = renderizar_boletim(_consolidada(), data_base=date(2026, 7, 24))
        boletim_2 = renderizar_boletim(consolidada_2, data_base=date(2026, 8, 1))

        assert DISCLAIMER_PADRAO in boletim_1
        assert DISCLAIMER_PADRAO in boletim_2
