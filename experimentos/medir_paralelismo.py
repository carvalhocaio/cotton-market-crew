"""Experimento exploratório: fan-in paralelo reduz wall-clock de verdade?

Não é testável com TDD tradicional (mede tempo de execução real). Roda
duas vezes a mesma Crew — uma paralela, uma forçada síncrona — e compara.
Não entra em `make check` nem em CI. Faz 10 chamadas reais de LLM.

Uso:
    PYTHONPATH=src uv run python experimentos/medir_paralelismo.py
"""

import os
import time

from crewai import LLM, Crew

from cotton_market_crew.pipeline import montar_pipeline
from cotton_market_crew.store import MercadoStore


def forcar_execucao_sequencial(crew: Crew) -> Crew:
    """Desliga async_execution nas tasks upstream da mesma Crew montada.

    Reaproveita `montar_pipeline` como única fonte de verdade sobre como
    a pipeline é composta; só o campo medido neste experimento muda.
    """
    for task in crew.tasks[:-1]:
        task.async_execution = False
    return crew


def medir(nome: str, crew: Crew) -> None:
    inicio = time.perf_counter()
    crew.kickoff()
    duracao = time.perf_counter() - inicio

    print(f"\n{'=' * 60}\n{nome}\n{'=' * 60}")
    print(f"Wall-clock: {duracao:.2f}s")
    print(f"Uso de tokens: {crew.usage_metrics}")


def main() -> None:
    llm = LLM(
        model="gemini/gemini-2.5-flash",
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0.2,
    )
    store = MercadoStore()

    crew_paralela = montar_pipeline(store, llm)
    medir("PARALELA (async_execution=True nas 4 tasks upstream)", crew_paralela)

    crew_sequencial = forcar_execucao_sequencial(montar_pipeline(store, llm))
    medir("SEQUENCIAL (async_execution=False em todas)", crew_sequencial)


if __name__ == "__main__":
    main()
