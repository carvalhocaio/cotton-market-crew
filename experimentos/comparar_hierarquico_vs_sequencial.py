"""Experimento: Process.hierarchical vale o custo do gerente?

O pipeline sequencial com guardrails já foi medido no Bloco 5:
85 successful_requests (ver ADR-005). Este experimento roda só o
hierárquico e compara contra aquele número de referência — não repete
o sequencial, para não duplicar custo de um dado que já temos.

Não é testável com TDD tradicional. Roda uma vez. Não entra em `make
check`. Aviso: esta é a rodada mais cara do projeto até aqui — a
sequencial de referência já custou 85 chamadas; espere igual ou mais.

Uso:
    PYTHONPATH=src uv run python experimentos/comparar_hierarquico_vs_sequencial.py
"""

import os
import time

from crewai import LLM

from cotton_market_crew.pipeline import montar_pipeline_hierarquico
from cotton_market_crew.store import MercadoStore

REQUESTS_SEQUENCIAL_REFERENCIA = 85  # ver ADR-005


def main() -> None:
    llm = LLM(
        model="gemini/gemini-2.5-flash",
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0.2,
    )
    store = MercadoStore()
    crew = montar_pipeline_hierarquico(store, llm)

    inicio = time.perf_counter()
    resultado = crew.kickoff()
    duracao = time.perf_counter() - inicio

    print(f"\n{'=' * 60}\nBOLETIM CONSOLIDADO (HIERÁRQUICO)\n{'=' * 60}")
    print(resultado.pydantic)

    print(f"\nWall-clock: {duracao:.2f}s")
    print(f"Uso de tokens: {crew.usage_metrics}")

    requests_hierarquico = crew.usage_metrics.successful_requests
    diferenca_pct = (
        (requests_hierarquico - REQUESTS_SEQUENCIAL_REFERENCIA)
        / REQUESTS_SEQUENCIAL_REFERENCIA
        * 100
    )

    print(f"\n{'=' * 60}\nCOMPARAÇÃO\n{'=' * 60}")
    print(
        f"Sequencial (referência, ADR-005): {REQUESTS_SEQUENCIAL_REFERENCIA} chamadas"
    )
    print(f"Hierárquico (esta rodada):        {requests_hierarquico} chamadas")
    print(f"Diferença:                         {diferenca_pct:+.1f}%")


if __name__ == "__main__":
    main()
