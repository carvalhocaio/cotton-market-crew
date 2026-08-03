from decimal import Decimal

from crewai.tasks.task_output import TaskOutput

from cotton_market_crew.esquemas import AnaliseConsolidada, AnaliseFisico
from cotton_market_crew.guardrails import (
    criar_guardrail_basis_numerico,
    guardrail_compliance,
)


def _output(basis_cents_lb: float) -> TaskOutput:
    analise = AnaliseFisico(
        regiao="MT",
        tendencia="alta",
        basis_cents_lb=basis_cents_lb,
        comentario="Basis positivo indicando forte demanda na região.",
    )
    return TaskOutput(description="desc", agent="agente-teste", pydantic=analise)


def _output_consolidada(comentario: str) -> TaskOutput:
    analise = AnaliseConsolidada(
        tendencia_geral="alta",
        regiao_destaque="MT",
        basis_medio_cents_lb=15.20,
        comentario_estrategico=comentario,
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


class TestGuardrailCompliance:
    def test_aceita_comentario_descritivo_sem_recomendacao(self):
        sucesso, resultado = guardrail_compliance(
            _output_consolidada(
                "Basis firme nas três praças reforça viés de alta para o "
                "físico, com destaque para Mato Grosso no curto prazo."
            )
        )

        assert sucesso is True

    def test_aceita_comentario_que_menciona_cambio_de_venda(self):
        """Não pode dar falso positivo em vocabulário legítimo do domínio."""
        sucesso, resultado = guardrail_compliance(
            _output_consolidada(
                "O câmbio de venda depreciado favorece a competitividade "
                "do algodão brasileiro exportado no curto prazo."
            )
        )

        assert sucesso is True

    def test_rejeita_recomendacao_de_compra(self):
        sucesso, mensagem = guardrail_compliance(
            _output_consolidada(
                "Diante do cenário, recomendamos comprar algodão agora "
                "para travar o preço atual."
            )
        )

        assert sucesso is False
        assert "recomendamos comprar" in mensagem.lower()

    def test_rejeita_recomendacao_de_venda(self):
        sucesso, mensagem = guardrail_compliance(
            _output_consolidada("É hora de vender antes que o preço caia.")
        )

        assert sucesso is False

    def test_rejeita_linguagem_de_garantia(self):
        sucesso, mensagem = guardrail_compliance(
            _output_consolidada(
                "Este é um cenário garantido de valorização nas próximas semanas."
            )
        )

        assert sucesso is False

    def test_rejeita_saida_sem_output_pydantic(self):
        output_sem_pydantic = TaskOutput(description="desc", agent="agente-teste")

        sucesso, mensagem = guardrail_compliance(output_sem_pydantic)

        assert sucesso is False
        assert "output_pydantic" in mensagem.lower()
