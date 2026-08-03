from cotton_market_crew.pipeline import montar_pipeline
from crewai import Crew, Process

from cotton_market_crew.store import MercadoStore


class TestMontarPipeline:
    def test_retorna_instancia_de_crew(self, llm_falso):
        store = MercadoStore()

        crew = montar_pipeline(store, llm_falso)

        assert isinstance(crew, Crew)

    def test_cria_cinco_agentes(self, llm_falso):
        store = MercadoStore()

        crew = montar_pipeline(store, llm_falso)

        assert len(crew.agents) == 5

    def test_cria_cinco_tasks(self, llm_falso):
        store = MercadoStore()

        crew = montar_pipeline(store, llm_falso)

        assert len(crew.tasks) == 5

    def test_quatro_tasks_upstream_sao_assincronas(self, llm_falso):
        store = MercadoStore()

        crew = montar_pipeline(store, llm_falso)

        tasks_assincronas = [t for t in crew.tasks if t.async_execution]
        assert len(tasks_assincronas) == 4

    def test_task_de_consolidacao_e_sincrona_e_usa_context(self, llm_falso):
        store = MercadoStore()

        crew = montar_pipeline(store, llm_falso)

        task_consolidacao = crew.tasks[-1]

        assert task_consolidacao.async_execution is False
        assert len(task_consolidacao.context) == 4

    def test_processo_e_sequencial(self, llm_falso):
        store = MercadoStore()

        crew = montar_pipeline(store, llm_falso)

        assert crew.process == Process.sequential
