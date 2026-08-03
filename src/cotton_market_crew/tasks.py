"""Fábricas de Task do CrewAI.

Cada fábrica recebe os fatos de domínio já calculados (não o MercadoStore
inteiro) - por SRP, quem monta a Task só formata prompt e liga ao schema
de saída. Buscar os fatos no store é responsabilidade de quem orquestra o
pipeline.
"""

from crewai import Agent, Task

from cotton_market_crew.dominio import Basis, Cambio, CotacaoFutura, IndicadorFisico
from cotton_market_crew.esquemas import AnaliseFisico, AnaliseMercadoExterno


def criar_task_analise_fisico(
    agente: Agent,
    indicador: IndicadorFisico,
    cotacao: CotacaoFutura,
    basis: Basis,
) -> Task:
    """Monta a Task de análise do físico a partir de fatos já calculados."""
    description = (
        f"Analise o mercado físico de algodão na região {indicador.regiao} "
        f"com base nos seguintes fatos de mercado, referentes a "
        f"{indicador.data.isoformat()}:\n\n"
        f"- Indicador físico: R$ {indicador.reais_por_arroba:.2f} por arroba "
        f"(fonte: {indicador.fonte})\n"
        f"- Cotação futura ({cotacao.contrato}): "
        f"{cotacao.cents_por_libra:.2f} cents/lb (fonte: {cotacao.fonte})\n"
        f"- Basis calculado: {basis.valor_cents_por_libra:.2f} cents/lb\n\n"
        "Com base nesses números, determine a tendência de curto prazo "
        "(alta, queda ou estável) e escreva um comentário justificando a "
        "leitura. Não invente números que não estejam listados acima."
    )

    return Task(
        description=description,
        expected_output=(
            "Uma análise estruturada contendo região, tendência, o valor "
            "de basis em cents/lb e um comentário justificando a leitura."
        ),
        agent=agente,
        output_pydantic=AnaliseFisico,
    )


def criar_task_analise_mercado_externo(
    agente: Agent, cotacao: CotacaoFutura, cambio: Cambio
) -> Task:
    """Monta a Task de análise do mercado externo (futuro ICE + câmbio)."""
    description = (
        f"Analise o mercado externo de algodão com base nos seguintes "
        f"fatos de mercado, referentes a {cotacao.data.isoformat()}:\n\n"
        f"- Cotação futura ({cotacao.contrato}): "
        f"{cotacao.cents_por_libra:.2f} cents/lb (fonte: {cotacao.fonte})\n"
        f"- Câmbio PTAX venda: R$ {cambio.ptax_venda:.4f}\n\n"
        "Com base nesses números, determine a tendência do contrato "
        "futuro (alta, queda ou estável) e se o câmbio atual é favorável, "
        "desfavorável ou neutro para a competitividade do algodão "
        "brasileiro exportado. Escreva um comentário justificando a "
        "leitura. Não invente números que não estejam listados acima."
    )

    return Task(
        description=description,
        expected_output=(
            "Uma análise estruturada contendo a tendência do futuro, a "
            "pressão cambial e um comentário justificando a leitura."
        ),
        agent=agente,
        output_pydantic=AnaliseMercadoExterno,
    )
