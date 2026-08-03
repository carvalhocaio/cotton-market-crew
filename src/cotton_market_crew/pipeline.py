"""Monta a Crew completa do boletim semanal.

Fan-in paralelo: 3 analistas regionais + 1 de mercado externo rodam
assincronamente (`async_execution=True`); o estrategista consolida de
forma síncrona via `context`. `Process.sequential` com tasks assíncronas
é o padrão do CrewAI pra isso — o processo aguarda todas as tasks
assíncronas pendentes antes de rodar a próxima task síncrona.

`async_execution` é setado aqui, não nas fábricas de `tasks.py` — é uma
decisão de orquestração (como a task roda), não de conteúdo (o que ela
faz).

Desde o ADR-004, os analistas físicos recebem o câmbio bruto (PTAX), não
o basis pré-calculado — precisam converter usando a ferramenta do Bloco 4.
`MercadoStore.calcular_basis` continua existindo e é usado como fonte de
verdade independente para o guardrail do Bloco 5, não é mais passado
direto pro prompt.
"""

from crewai import Crew, Process

from cotton_market_crew.agentes import (
    criar_analista_fisico,
    criar_analista_mercado_externo,
    criar_estrategista,
)
from cotton_market_crew.store import MercadoStore
from cotton_market_crew.tasks import (
    criar_task_analise_fisico,
    criar_task_analise_mercado_externo,
    criar_task_consolidacao,
)

REGIOES = ("MT", "BA", "GO")


def montar_pipeline(store: MercadoStore, llm: object) -> Crew:
    """Monta a Crew: analistas regionais + mercado externo em paralelo,
    estrategista consolidando o resultado."""
    agentes = []
    tasks_upstream = []

    cotacao = store.ultima_cotacao_futura()
    cambio = store.ultimo_cambio()

    for regiao in REGIOES:
        agente = criar_analista_fisico(llm)
        indicador = store.ultimo_indicador(regiao)

        task = criar_task_analise_fisico(agente, indicador, cotacao, cambio)
        task.async_execution = True

        agentes.append(agente)
        tasks_upstream.append(task)

    analista_externo = criar_analista_mercado_externo(llm)
    task_externo = criar_task_analise_mercado_externo(analista_externo, cotacao, cambio)
    task_externo.async_execution = True

    agentes.append(analista_externo)
    tasks_upstream.append(task_externo)

    estrategista = criar_estrategista(llm)
    task_consolidacao = criar_task_consolidacao(estrategista, tasks_upstream)
    agentes.append(estrategista)

    return Crew(
        agents=agentes,
        tasks=[*tasks_upstream, task_consolidacao],
        process=Process.sequential,
    )
