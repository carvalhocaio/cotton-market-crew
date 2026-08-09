"""Renderização determinística do boletim final.

O disclaimer e a data-base nunca passam pelo LLM — são texto fixo,
anexado aqui pelo Python (ver ADR-005: "não há o que validar em um
rodapé fixo"). Esta é a última milha do princípio que atravessa o
projeto inteiro desde o ADR-001: o LLM redige a análise, o Python
garante a estrutura e as partes que não podem variar.
"""

from datetime import date

from cotton_market_crew.esquemas import AnaliseConsolidada

DISCLAIMER_PADRAO = (
    "Este boletim é gerado a partir de dados sintéticos para fins de "
    "estudo e não representa cotações reais de mercado. Não constitui "
    "recomendação de compra, venda ou qualquer decisão de "
    "comercialização. Consulte sempre fontes oficiais (CEPEA/ESALQ, ICE "
    "Futures, BACEN) antes de qualquer decisão real."
)


def renderizar_boletim(consolidada: AnaliseConsolidada, data_base: date) -> str:
    """Monta o boletim final em markdown a partir da análise consolidada.

    `consolidada` já deve ter passado pelo guardrail de compliance antes
    de chegar aqui — esta função não valida conteúdo, só formata.
    """
    return (
        f"# Boletim de Mercado de Algodão\n\n"
        f"**Data-base:** {data_base.strftime('%d/%m/%Y')}\n\n"
        f"**Tendência geral:** {consolidada.tendencia_geral}\n"
        f"**Região de destaque:** {consolidada.regiao_destaque}\n"
        f"**Basis médio:** {consolidada.basis_medio_cents_lb:.2f} cents/lb\n\n"
        f"## Análise estratégica\n\n"
        f"{consolidada.comentario_estrategico}\n\n"
        f"---\n\n"
        f"*{DISCLAIMER_PADRAO}*\n"
    )
