"""Experimento exploratório: o jargão do backstory muda a saída do LLM?

Não é testável com TDD tradicional (a saída do LLM não é determinística).
Roda uma vez, compara manualmente. Não entra em `make check` nem em CI.

Uso:
    PYTHONPATH=src uv run python experimentos/comparar_backstory.py
"""

import os
from datetime import date
from decimal import Decimal

from crewai import LLM, Agent, Crew, Process

from cotton_market_crew.agentes import criar_analista_fisico
from cotton_market_crew.dominio import Basis, CotacaoFutura, IndicadorFisico
from cotton_market_crew.tasks import criar_task_analise_fisico

FATOS = {
    "indicador": IndicadorFisico(
        data=date(2026, 7, 24), regiao="MT", reais_por_arroba=Decimal("153.20")
    ),
    "cotacao": CotacaoFutura(
        data=date(2026, 7, 24), contrato="DEZ2026", cents_por_libra=Decimal("74.52")
    ),
    "basis": Basis(
        data=date(2026, 7, 24), regiao="MT", valor_cents_por_libra=Decimal("13.50")
    ),
}


def criar_analista_generico(llm: object) -> Agent:
    """Agente de controle: mesmo objetivo, sem jargão do domínio do algodão."""
    return Agent(
        role="Data Analyst",
        goal="Analyze the provider market data and determine the trend.",
        backstory=(
            "You are an experienced data analyst who reviews numeric data "
            "and writes clear, concise reports."
        ),
        allow_delegation=False,
        llm=llm,
    )


def rodar_com_agente(nome: str, agente: Agent) -> None:
    task = criar_task_analise_fisico(
        agente, FATOS["indicador"], FATOS["cotacao"], FATOS["basis"]
    )
    crew = Crew(agents=[agente], tasks=[task], process=Process.sequential)

    resultado = crew.kickoff()

    print(f"\n{'=' * 60}\nAGENTE: {nome}\n{'=' * 60}")
    print(resultado.pydantic)
    print(f"\nUso de tokens: {crew.usage_metrics}")


def main() -> None:
    llm = LLM(
        model="gemini/gemini-2.5-flash",
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0.2,
    )

    rodar_com_agente("Calibrado (jargão do domínio)", criar_analista_fisico(llm))
    rodar_com_agente("Genérico (controle)", criar_analista_generico(llm))


if __name__ == "__main__":
    main()
