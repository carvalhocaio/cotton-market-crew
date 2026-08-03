"""Tools do CrewAI expostas a partir de funções puras já existentes.

O agente decide quando chamar a conversão; o cálculo em si nunca passa
pelo LLM — é a materialização da nota deixada no ADR-001. A tool é uma
casca fina sobre `conversao.py`: não duplica lógica, só adapta o formato
de saída (string, pro LLM ler) em vez do `Decimal` que o código usa
internamente.
"""

from decimal import Decimal

from crewai.tools import tool

from cotton_market_crew.conversao import (
    ConversaoInvalidaError,
    arroba_reais_para_cents_libra,
)


@tool("Converter arroba para cents por libra")
def converter_arroba_para_cents_libra_tool(
    reais_por_arroba: float, ptax_venda: float
) -> str:
    """Converte um preço em R$/arroba de algodão físico para cents/lb,
    usando a taxa PTAX de venda informada. Use esta ferramenta sempre que
    precisar comparar um preço físico em R$/arroba com um preço futuro
    cotado em cents/lb — nunca faça essa conversão de cabeça."""
    try:
        resultado = arroba_reais_para_cents_libra(
            reais_por_arroba=Decimal(str(reais_por_arroba)),
            ptax_venda=Decimal(str(ptax_venda)),
        )
    except ConversaoInvalidaError as erro:
        return f"Erro: {erro}"
    return f"{resultado} cents/lb"
