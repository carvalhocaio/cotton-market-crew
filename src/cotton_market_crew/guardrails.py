"""Guardrails determinísticos sobre a saída dos agentes.

O LLM redige, o Python garante — mesmo princípio usado no LangGraph do
`cotton-claims-agent`, agora como primitivo de framework
(`Task(guardrail=...)`) em vez de gambiarra manual. Guardrails aqui não
usam IA para validar IA: comparam contra fatos calculados
independentemente pelo domínio (MercadoStore, conversao.py), a mesma
fonte de verdade usada nos testes.
"""

from collections.abc import Callable
from decimal import Decimal
from typing import Any

from crewai.tasks.task_output import TaskOutput

TOLERANCIA_CENTS_LB = Decimal("0.05")


def criar_guardrail_basis_numerico(
    basis_esperado: Decimal,
) -> Callable[[TaskOutput], tuple[bool, Any]]:
    """Cria um guardrail que rejeita basis divergente do calculado pelo Python.

    `basis_esperado` vem de `MercadoStore.calcular_basis`, calculado de
    forma determinística e independente da saída do LLM. É uma fábrica
    (não uma função direta) porque o valor de comparação só existe em
    tempo de execução do pipeline — a assinatura que o CrewAI espera
    (`Callable[[TaskOutput], tuple[bool, Any]]`) recebe só a saída, então
    o valor esperado precisa vir por closure.
    """

    def guardrail(output: TaskOutput) -> tuple[bool, Any]:
        analise = output.pydantic
        if analise is None:
            return False, "Saída sem output_pydantic; guardrail não pode validar."

        basis_reportado = Decimal(str(analise.basis_cents_lb))
        diferenca = abs(basis_reportado - basis_esperado)

        if diferenca > TOLERANCIA_CENTS_LB:
            return False, (
                f"Basis reportado ({basis_reportado:.2f} cents/lb) diverge do "
                f"calculado pelo MercadoStore ({basis_esperado:.2f} cents/lb) "
                f"em {diferenca:.2f} cents/lb, acima da tolerância de "
                f"{TOLERANCIA_CENTS_LB} cents/lb. Recalcule usando a "
                f"ferramenta de conversão."
            )
        return True, analise

    return guardrail
