"""Experimento exploratório: o agente usa a ferramenta de conversão de fato?

Evidência: comparar o basis que o agente devolveu contra o valor que
`MercadoStore.calcular_basis()` calcula de forma determinística pelos
mesmos dados. Se bater com precisão de centavos, é evidência forte de uso
real da ferramenta — LLM não acerta essa conta de cabeça com essa
precisão de forma confiável.

Não é testável com TDD tradicional. Roda uma vez, uma chamada real de LLM.

Uso:
    PYTHONPATH=src uv run python experimentos/verificar_uso_da_ferramenta.py
"""

import os

from crewai import LLM, Crew, Process

from cotton_market_crew.agentes import criar_analista_fisico
from cotton_market_crew.store import MercadoStore
from cotton_market_crew.tasks import criar_task_analise_fisico

REGIAO = "MT"


def main() -> None:
    llm = LLM(
        model="gemini/gemini-2.5-flash",
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0.2,
    )
    store = MercadoStore()

    indicador = store.ultimo_indicador(REGIAO)
    cotacao = store.ultima_cotacao_futura()
    cambio = store.ultimo_cambio()
    basis_esperado = store.calcular_basis(REGIAO)

    agente = criar_analista_fisico(llm)
    task = criar_task_analise_fisico(agente, indicador, cotacao, cambio)
    crew = Crew(agents=[agente], tasks=[task], process=Process.sequential)

    resultado = crew.kickoff()
    analise = resultado.pydantic

    diferenca = abs(
        float(basis_esperado.valor_cents_por_libra) - analise.basis_cents_lb
    )

    print(f"\n{'=' * 60}\nRESULTADO\n{'=' * 60}")
    print(
        f"Basis calculado pelo Python (MercadoStore): "
        f"{basis_esperado.valor_cents_por_libra} cents/lb"
    )
    print(
        f"Basis reportado pelo agente:                {analise.basis_cents_lb} cents/lb"
    )
    print(f"Diferença absoluta:                          {diferenca:.4f}")
    print(f"\nTendência: {analise.tendencia}")
    print(f"Comentário: {analise.comentario}")
    print(f"\nUso de tokens: {crew.usage_metrics}")

    if diferenca < 0.05:
        print("\n Bateu com precisão de centavos. Forte indício de uso da ferramenta.")
    else:
        print(
            "\n Divergência real. Agente pode ter calculado de cabeça ou errado a tool."
        )


if __name__ == "__main__":
    main()
