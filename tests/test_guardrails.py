from decimal import Decimal

from crewai.tasks.task_output import TaskOutput

from cotton_market_crew.esquemas import AnaliseFisico
from cotton_market_crew.guardrails import criar_guardrail_basis_numerico


def _output(basis_cents_lb: float) -> TaskOutput:
    analise = AnaliseFisico(
        regiao="MT",
        tendencia="alta",
        basis_cents_lb=basis_cents_lb,
        comentario="Basis positivo indicando forte demanda na região.",
    )
    return TaskOutput(description="desc", agent="agente-teste", pydantic=analise)


class TestCriarGuardrailBasisNumerico:
    def test_aceita_basis_identico(self):
        guardrail = criar_guardrail_basis_numerico(Decimal("14.27"))

        sucesso, resultado = guardrail(_output(14.27))

        assert sucesso is True
        assert resultado.basis_cents_lb == 14.27

    def test_aceita_diferenca_dentro_da_tolerancia(self):
        guardrail = criar_guardrail_basis_numerico(Decimal("14.27"))

        sucesso, _ = guardrail(_output(14.29))

        assert sucesso is True

    def test_rejeita_diferenca_acima_da_tolerancia(self):
        guardrail = criar_guardrail_basis_numerico(Decimal("14.27"))

        sucesso, mensagem = guardrail(_output(18.00))

        assert sucesso is False
        assert "14.27" in mensagem
        assert "18.00" in mensagem

    def test_rejeita_saida_sem_output_pydantic(self):
        guardrail = criar_guardrail_basis_numerico(Decimal("14.27"))
        output_sem_pydantic = TaskOutput(description="desc", agent="agente-teste")

        sucesso, mensagem = guardrail(output_sem_pydantic)

        assert sucesso is False
        assert "output_pydantic" in mensagem.lower()
