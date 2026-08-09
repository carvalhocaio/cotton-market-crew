"""Monta a Crew completa do boletim semanal.

Dois pipelines disponíveis: `montar_pipeline` (sequencial, fan-in
paralelo via async_execution) e `montar_pipeline_hierarquico`
(Process.hierarchical, com um gerente decidindo a quem delegar). Ambos
reaproveitam `_montar_analistas_e_tasks_upstream` — os 4 analistas e seus
guardrails numéricos são idênticos nos dois casos; só muda como a Crew
final é montada.

`async_execution` é setado aqui, não nas fábricas de `tasks.py` — é uma
decisão de orquestração (como a task roda), não de conteúdo (o que ela
faz).

Desde o ADR-004, os analistas físicos recebem o câmbio bruto (PTAX), não
o basis pré-calculado — precisam converter usando a ferramenta do Bloco 4.
`MercadoStore.calcular_basis` alimenta o guardrail numérico (Bloco 5): a
mesma fonte de verdade usada para montar o prompt em versões anteriores
agora valida a saída do agente, em vez de ser entregue pronta.

No pipeline hierárquico, `Process.hierarchical` ignora `task.agent` para
decidir quem executa — o `manager_agent` sempre executa (delegando aos
demais quando decide), então as tasks upstream ficam deliberadamente
síncronas aqui, isolando a variável sob teste (tipo de processo) da
variável já medida no Bloco 3 (paralelismo). Ver ADR-006.
"""

from crewai import Crew, Process, Task

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


def _montar_analistas_e_tasks_upstream(
    store: MercadoStore, llm: object
) -> tuple[list, list[Task]]:
    """Monta os 4 analistas (3 regionais + 1 externo) e suas tasks, já
    com o guardrail numérico aplicado nas físicas. Compartilhado entre
    os pipelines sequencial e hierárquico."""
    agentes = []
    tasks_upstream = []

    cotacao = store.ultima_cotacao_futura()
    cambio = store.ultimo_cambio()

    for regiao in REGIOES:
        agente = criar_analista_fisico(llm)
        indicador = store.ultimo_indicador(regiao)
        basis_esperado = store.calcular_basis(regiao).valor_cents_por_libra

        task = criar_task_analise_fisico(agente, indicador, cotacao, cambio)
        task.guardrail = criar_guardrail_basis_numerico(basis_esperado)

        agentes.append(agente)
        tasks_upstream.append(task)

    analista_externo = criar_analista_mercado_externo(llm)
    task_externo = criar_task_analise_mercado_externo(analista_externo, cotacao, cambio)

    agentes.append(analista_externo)
    tasks_upstream.append(task_externo)

    return agentes, tasks_upstream


def montar_pipeline(store: MercadoStore, llm: object) -> Crew:
    """Monta a Crew sequencial: analistas em paralelo (async_execution),
    estrategista consolidando via context, guardrails determinísticos."""
    agentes, tasks_upstream = _montar_analistas_e_tasks_upstream(store, llm)

    for task in tasks_upstream:
        task.async_execution = True

    estrategista = criar_estrategista(llm)
    task_consolidacao = criar_task_consolidacao(estrategista, tasks_upstream)
    task_consolidacao.guardrail = guardrail_compliance
    agentes.append(estrategista)

    return Crew(
        agents=agentes,
        tasks=[*tasks_upstream, task_consolidacao],
        process=Process.sequential,
    )


def montar_pipeline_hierarquico(store: MercadoStore, llm: object) -> Crew:
    """Monta a Crew hierárquica: um gerente decide a quem delegar cada
    task, em vez de agent fixo por task. O estrategista vira o
    `manager_agent` — não entra na lista `agents` nem pode ter tools,
    restrições do CrewAI para o papel de gerente."""
    agentes, tasks_upstream = _montar_analistas_e_tasks_upstream(store, llm)

    gerente = criar_estrategista(llm)
    task_consolidacao = criar_task_consolidacao(gerente, tasks_upstream)
    task_consolidacao.guardrail = guardrail_compliance

    return Crew(
        agents=agentes,
        tasks=[*tasks_upstream, task_consolidacao],
        process=Process.hierarchical,
        manager_agent=gerente,
    )
