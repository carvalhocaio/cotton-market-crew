from cotton_market_crew.ferramentas import converter_arroba_para_cents_libra_tool


class TestConverterArrobaParaCentsLibraTool:
    def test_tem_nome_descritivo(self):
        assert converter_arroba_para_cents_libra_tool.name == (
            "Converter arroba para cents por libra"
        )

    def test_description_orienta_quando_usar(self):
        descricao = converter_arroba_para_cents_libra_tool.description.lower()

        assert "arroba" in descricao
        assert "cents" in descricao

    def test_converte_valor_conhecido(self):
        resultado = converter_arroba_para_cents_libra_tool.run(
            reais_por_arroba=158.50, ptax_venda=5.3421
        )

        assert "89.72" in resultado

    def test_retorna_mensagem_de_erro_sem_lancar_excecao(self):
        resultado = converter_arroba_para_cents_libra_tool.run(
            reais_por_arroba=0, ptax_venda=5.3421
        )

        assert "erro" in resultado.lower()
