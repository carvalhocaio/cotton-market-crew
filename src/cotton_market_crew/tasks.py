"""Fábricas de Task do CrewAI.

Cada fábrica recebe os fatos de domínio já calculados (não o MercadoStore
inteiro) — por SRP, quem monta a Task só formata prompt e liga ao schema
de saída. Buscar os fatos no store é responsabilidade de quem orquestra o
pipeline (Bloco 3).

A Task de análise física recebe o câmbio bruto (PTAX), não o basis já
calculado (ver ADR-004): o agente precisa converter R$/arroba para
cents/lb usando a ferramenta antes de poder comparar com o futuro — isso
é o que faz `converter_arroba_para_cents_libra_tool` (Bloco 4) ser
realmente usada, em vez de existir só estruturalmente.
"""

from crewai import Agent, Task

from cotton_market_crew.dominio import Cambio, CotacaoFutura, IndicadorFisico
from cotton_market_crew.esquemas import (
    AnaliseConsolidada,
    AnaliseFisico,
    AnaliseMercadoExterno,
)


def criar_task_analise_fisico(
    agente: Agent,
    indicador: IndicadorFisico,
    cotacao: CotacaoFutura,
    cambio: Cambio,
) -> Task:
    """Monta a Task de análise do físico a partir de fatos brutos.

    O agente recebe o preço físico em R$/arroba, o futuro em cents/lb e a
    PTAX — não o basis pronto. Precisa calcular o basis usando a
    ferramenta de conversão antes de poder responder.
    """
    description = (
        f"Analise o mercado físico de algodão na região {indicador.regiao} "
        f"com base nos seguintes fatos de mercado, referentes a "
        f"{indicador.data.isoformat()}:\n\n"
        f"- Indicador físico: R$ {indicador.reais_por_arroba:.2f} por arroba "
        f"(fonte: {indicador.fonte})\n"
        f"- Cotação futura ({cotacao.contrato}): "
        f"{cotacao.cents_por_libra:.2f} cents/lb (fonte: {cotacao.fonte})\n"
        f"- Câmbio PTAX venda: R$ {cambio.ptax_venda:.4f}\n\n"
        "O indicador físico está em R$/arroba e o futuro está em "
        "cents/lb — unidades diferentes, não comparáveis diretamente. "
        "Use a ferramenta de conversão para transformar o indicador "
        "físico em cents/lb antes de calcular o basis (físico convertido "
        "menos futuro). Não faça essa conta de cabeça. Com o basis "
        "calculado, determine a tendência de curto prazo (alta, queda ou "
        "estável) e escreva um comentário justificando a leitura. Não "
        "invente números que não estejam listados acima ou que não "
        "venham do resultado da ferramenta."
    )

    return Task(
        description=description,
        expected_output=(
            "Uma análise estruturada contendo região, tendência, o valor "
            "de basis em cents/lb calculado com a ferramenta, e um "
            "comentário justificando a leitura."
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


def criar_task_consolidacao(agente: Agent, tasks_upstream: list[Task]) -> Task:
    """Monta a Task do estrategista, consolidando as análises upstream.

    O CrewAI injeta a saída de cada Task em `tasks_upstream` no prompt via
    `context` — não repetimos números aqui, só instruímos o que fazer com
    o que já foi produzido pelos analistas.
    """
    description = (
        "Com base nas análises de mercado físico e mercado externo "
        "produzidas pelos analistas, consolide uma leitura de risco única "
        "para o boletim semanal. Aponte a tendência geral, a região que "
        "mais chama atenção e calcule o basis médio entre as regiões "
        "analisadas. Escreva um comentário estratégico que resolva "
        "eventuais sinais conflitantes entre o físico e o externo, sem "
        "recomendar compra ou venda — apenas descreva o risco."
    )

    return Task(
        description=description,
        expected_output=(
            "Uma análise consolidada contendo a tendência geral, a região "
            "de destaque, o basis médio em cents/lb e um comentário "
            "estratégico."
        ),
        agent=agente,
        context=tasks_upstream,
        output_pydantic=AnaliseConsolidada,
    )
