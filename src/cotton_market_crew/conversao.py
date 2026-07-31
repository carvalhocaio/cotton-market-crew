"""Conversão de unidades entre o mercado físico brasileiro e o futuro ICE.

Isolada como função pura e determinística de propósito: essa é a conta que
um LLM erra com confiança. No Bloco 4 esta função vira uma tool do CrewAI —
o agente decide *quando* converter, o Python garante *como*.
"""

from decimal import ROUND_HALF_UP, Decimal


class ConversaoInvalidaError(ValueError):
    """Levantado quando os parâmetros de conversão são inválidos."""


KG_POR_LB = Decimal("0.45359237")
KG_POR_ARROBA = Decimal("15")
DUAS_CASAS = Decimal("0.01")


def arroba_reais_para_cents_libra(
    reais_por_arroba: Decimal, ptax_venda: Decimal
) -> Decimal:
    """Converte R$/arroba (mercado físico) para cents/lb (base ICE).

    Cadeia: R$/@ -> R$/kg -> R$/lb -> US$/lb -> cents/lb.
    """
    if reais_por_arroba <= 0:
        raise ConversaoInvalidaError(
            f"reais_por_arroba deve ser positivo, recebido: {reais_por_arroba}."
        )
    if ptax_venda <= 0:
        raise ConversaoInvalidaError(
            f"ptax_venda deve ser positivo, recebido: {ptax_venda}."
        )

    reais_por_kg = reais_por_arroba / KG_POR_ARROBA
    reais_por_lb = reais_por_kg * KG_POR_LB
    dolar_por_lb = reais_por_lb / ptax_venda
    cents_por_lb = dolar_por_lb * 100

    return cents_por_lb.quantize(DUAS_CASAS, rounding=ROUND_HALF_UP)
