"""Ponto de entrada: gera o boletim semanal completo.

Uso:
    uv run python main.py

Requer GEMINI_API_KEY no ambiente. Roda o pipeline sequencial completo
com guardrails (ver ADR-005 para o custo esperado: ~85 chamadas de LLM)
e imprime o boletim final renderizado — disclaimer e data-base sempre
anexados pelo Python, nunca gerados pelo LLM (ver ADR-005 e boletim.py).
"""

import os

from crewai import LLM

from cotton_market_crew.boletim import renderizar_boletim
from cotton_market_crew.pipeline import montar_pipeline
from cotton_market_crew.store import MercadoStore


def main() -> None:
    llm = LLM(
        model="gemini/gemini-2.5-flash",
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0.2,
    )
    store = MercadoStore()
    crew = montar_pipeline(store, llm)

    resultado = crew.kickoff()
    data_base = store.ultima_cotacao_futura().data

    boletim = renderizar_boletim(resultado.pydantic, data_base=data_base)

    print(boletim)
    print(f"\n(Uso de tokens: {crew.usage_metrics})")


if __name__ == "__main__":
    main()
