from crewai import Crew, Process
from crewai.tasks.task_output import TaskOutput

from cotton_market_crew.esquemas import AnaliseConsolidada, AnaliseFisico
from cotton_market_crew.pipeline import montar_pipeline
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


class TestMontarPipelineComGuardrails:
    def test_tasks_fisico_tem_guardrail_numerico_correto(self, llm_falso):
        store = MercadoStore()
        crew = montar_pipeline(store, llm_falso)

        for indice, regiao in enumerate(("MT", "BA", "GO")):
            task = crew.tasks[indice]
            basis_esperado = store.calcular_basis(regiao).valor_cents_por_libra

            output = TaskOutput(
                description="d",
                agent="a",
                pydantic=AnaliseFisico(
                    regiao=regiao,
                    tendencia="alta",
                    basis_cents_lb=float(basis_esperado),
                    comentario="Comentário de teste com tamanho suficiente.",
                ),
            )

            sucesso, _ = task.guardrail(output)

            assert sucesso is True

    def test_task_consolidacao_tem_guardrail_compliance(self, llm_falso):
        store = MercadoStore()
        crew = montar_pipeline(store, llm_falso)
        task_consolidacao = crew.tasks[-1]

        output = TaskOutput(
            description="d",
            agent="a",
            pydantic=AnaliseConsolidada(
                tendencia_geral="alta",
                regiao_destaque="MT",
                basis_medio_cents_lb=15.0,
                comentario_estrategico="Recomendamos comprar imediatamente.",
            ),
        )

        sucesso, _ = task_consolidacao.guardrail(output)

        assert sucesso is False
