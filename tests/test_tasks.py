# tests/test_tasks.py
from datetime import date
from decimal import Decimal

from crewai import Task

from cotton_market_crew.dominio import Basis, Cambio, CotacaoFutura, IndicadorFisico
from cotton_market_crew.esquemas import (
    AnaliseConsolidada,
    AnaliseFisico,
    AnaliseMercadoExterno,
)
from cotton_market_crew.tasks import (
    criar_task_analise_fisico,
    criar_task_analise_mercado_externo,
    criar_task_consolidacao,
)


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


class TestCriarTaskAnaliseMercadoExterno:
    def _fatos(self):
        cotacao = CotacaoFutura(
            data=date(2026, 7, 24),
            contrato="DEZ26",
            cents_por_libra=Decimal("74.52"),
        )
        cambio = Cambio(data=date(2026, 7, 24), ptax_venda=Decimal("5.2173"))
        return cotacao, cambio

    def test_retorna_instancia_de_task(self, llm_falso):
        from cotton_market_crew.agentes import criar_analista_mercado_externo

        agente = criar_analista_mercado_externo(llm=llm_falso)
        cotacao, cambio = self._fatos()

        task = criar_task_analise_mercado_externo(agente, cotacao, cambio)

        assert isinstance(task, Task)

    def test_usa_output_pydantic_correto(self, llm_falso):
        from cotton_market_crew.agentes import criar_analista_mercado_externo

        agente = criar_analista_mercado_externo(llm=llm_falso)
        cotacao, cambio = self._fatos()

        task = criar_task_analise_mercado_externo(agente, cotacao, cambio)

        assert task.output_pydantic is AnaliseMercadoExterno

    def test_description_contem_os_fatos_de_mercado(self, llm_falso):
        from cotton_market_crew.agentes import criar_analista_mercado_externo

        agente = criar_analista_mercado_externo(llm=llm_falso)
        cotacao, cambio = self._fatos()

        task = criar_task_analise_mercado_externo(agente, cotacao, cambio)

        assert "74.52" in task.description
        assert "5.2173" in task.description

    def test_agente_associado_e_o_recebido(self, llm_falso):
        from cotton_market_crew.agentes import criar_analista_mercado_externo

        agente = criar_analista_mercado_externo(llm=llm_falso)
        cotacao, cambio = self._fatos()

        task = criar_task_analise_mercado_externo(agente, cotacao, cambio)

        assert task.agent is agente


class TestCriarTaskConsolidacao:
    def _tasks_upstream(self, llm_falso):
        from cotton_market_crew.agentes import (
            criar_analista_fisico,
            criar_analista_mercado_externo,
        )

        analista_fisico = criar_analista_fisico(llm=llm_falso)
        analista_externo = criar_analista_mercado_externo(llm=llm_falso)

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
        cambio = Cambio(data=date(2026, 7, 24), ptax_venda=Decimal("5.2173"))

        task_fisico = criar_task_analise_fisico(
            analista_fisico, indicador, cotacao, basis
        )
        task_externo = criar_task_analise_mercado_externo(
            analista_externo, cotacao, cambio
        )
        return [task_fisico, task_externo]

    def test_retorna_instancia_de_task(self, llm_falso):
        from cotton_market_crew.agentes import criar_estrategista

        estrategista = criar_estrategista(llm=llm_falso)
        tasks_upstream = self._tasks_upstream(llm_falso)

        task = criar_task_consolidacao(estrategista, tasks_upstream)

        assert isinstance(task, Task)

    def test_context_contem_as_tasks_upstream(self, llm_falso):
        from cotton_market_crew.agentes import criar_estrategista

        estrategista = criar_estrategista(llm=llm_falso)
        tasks_upstream = self._tasks_upstream(llm_falso)

        task = criar_task_consolidacao(estrategista, tasks_upstream)

        assert task.context == tasks_upstream

    def test_usa_output_pydantic_correto(self, llm_falso):
        from cotton_market_crew.agentes import criar_estrategista

        estrategista = criar_estrategista(llm=llm_falso)
        tasks_upstream = self._tasks_upstream(llm_falso)

        task = criar_task_consolidacao(estrategista, tasks_upstream)

        assert task.output_pydantic is AnaliseConsolidada

    def test_agente_associado_e_o_estrategista(self, llm_falso):
        from cotton_market_crew.agentes import criar_estrategista

        estrategista = criar_estrategista(llm=llm_falso)
        tasks_upstream = self._tasks_upstream(llm_falso)

        task = criar_task_consolidacao(estrategista, tasks_upstream)

        assert task.agent is estrategista
