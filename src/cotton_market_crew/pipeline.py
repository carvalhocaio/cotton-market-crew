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
`MercadoStore.calcular_basis` continua existindo e agora alimenta o
guardrail numérico (Bloco 5): a mesma fonte de verdade usada para montar
o prompt original nas versões anteriores agora valida a saída do agente,
em vez de ser entregue pronta.

Guardrails: as 3 tasks físicas ganham checagem numérica contra o basis
calculado pelo Python; a task de consolidação ganha checagem de
compliance. A task de mercado externo fica sem guardrail — sua saída não
tem um valor numérico contínuo comparável contra o MercadoStore (ver
ADR-005).
"""

from crewai import Crew, Process

from cotton_market_crew.agentes import (
    criar_analista_fisico,
    criar_analista_mercado_externo,
    criar_estrategista,
)
from cotton_market_crew.guardrails import (
    criar_guardrail_basis_numerico,
    guardrail_compliance,
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
    estrategista consolidando o resultado, com guardrails determinísticos."""
    agentes = []
    tasks_upstream = []

    cotacao = store.ultima_cotacao_futura()
    cambio = store.ultimo_cambio()

    for regiao in REGIOES:
        agente = criar_analista_fisico(llm)
        indicador = store.ultimo_indicador(regiao)
        basis_esperado = store.calcular_basis(regiao).valor_cents_por_libra

        task = criar_task_analise_fisico(agente, indicador, cotacao, cambio)
        task.async_execution = True
        task.guardrail = criar_guardrail_basis_numerico(basis_esperado)

        agentes.append(agente)
        tasks_upstream.append(task)

    analista_externo = criar_analista_mercado_externo(llm)
    task_externo = criar_task_analise_mercado_externo(analista_externo, cotacao, cambio)
    task_externo.async_execution = True

    agentes.append(analista_externo)
    tasks_upstream.append(task_externo)

    estrategista = criar_estrategista(llm)
    task_consolidacao = criar_task_consolidacao(estrategista, tasks_upstream)
    task_consolidacao.guardrail = guardrail_compliance
    agentes.append(estrategista)

    return Crew(
        agents=agentes,
        tasks=[*tasks_upstream, task_consolidacao],
        process=Process.sequential,
    )
