# tests/test_tasks.py
from datetime import date
from decimal import Decimal

from crewai import Task

from cotton_market_crew.dominio import Basis, CotacaoFutura, IndicadorFisico
from cotton_market_crew.esquemas import AnaliseFisico
from cotton_market_crew.tasks import criar_task_analise_fisico


class TestCriarTaskAnaliseFisico:
    def _fatos(self):
        indicador = IndicadorFisico(
            data=date(2026, 7, 24),
            regiao="MT",
            reais_por_arroba=Decimal("153.20"),
        )
        cotacao = CotacaoFutura(
            data=date(2026, 7, 24),
            contrato="DEZ26",
            cents_por_libra=Decimal("74.52"),
        )
        basis = Basis(
            data=date(2026, 7, 24),
            regiao="MT",
            valor_cents_por_libra=Decimal("13.50"),
        )
        return indicador, cotacao, basis

    def test_retorna_instancia_de_task(self, llm_falso):
        from cotton_market_crew.agentes import criar_analista_fisico

        agente = criar_analista_fisico(llm=llm_falso)
        indicador, cotacao, basis = self._fatos()

        task = criar_task_analise_fisico(agente, indicador, cotacao, basis)

        assert isinstance(task, Task)

    def test_usa_output_pydantic_correto(self, llm_falso):
        from cotton_market_crew.agentes import criar_analista_fisico

        agente = criar_analista_fisico(llm=llm_falso)
        indicador, cotacao, basis = self._fatos()

        task = criar_task_analise_fisico(agente, indicador, cotacao, basis)

        assert task.output_pydantic is AnaliseFisico

    def test_description_contem_os_fatos_de_mercado(self, llm_falso):
        from cotton_market_crew.agentes import criar_analista_fisico

        agente = criar_analista_fisico(llm=llm_falso)
        indicador, cotacao, basis = self._fatos()

        task = criar_task_analise_fisico(agente, indicador, cotacao, basis)

        assert "153.20" in task.description
        assert "74.52" in task.description
        assert "MT" in task.description

    def test_agente_associado_e_o_recebido(self, llm_falso):
        from cotton_market_crew.agentes import criar_analista_fisico

        agente = criar_analista_fisico(llm=llm_falso)
        indicador, cotacao, basis = self._fatos()

        task = criar_task_analise_fisico(agente, indicador, cotacao, basis)

        assert task.agent is agente
