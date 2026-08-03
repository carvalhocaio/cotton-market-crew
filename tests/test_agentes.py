import pytest
from crewai import Agent
from crewai.llm import BaseLLM

from cotton_market_crew.agentes import criar_analista_fisico

class LLMFalso(BaseLLM):
    """Duplo de teste: satisfaz o contrato de BaseLLM sem chamar API real."""

    def __init__(self) -> None:
        super().__init__(model="falso/modelo-de-teste")

    def call(self, *args, **kwargs):
        return "resposta falsa"

@pytest.fixture
def llm_falso() -> LLMFalso:
    return LLMFalso()

class TestCriarAnalistaFisico:
    def test_retorna_instancia_de_agente(self, llm_falso: LLMFalso):
        agente = criar_analista_fisico(llm=llm_falso)

        assert isinstance(agente, Agent)

    def test_role_reflete_o_dominio(self, llm_falso: LLMFalso):
        agente = criar_analista_fisico(llm=llm_falso)

        assert "físico" in agente.role.lower()
        assert "algodão" in agente.role.lower()

    def test_goal_menciona_basis_e_tendencia(self, llm_falso: LLMFalso):
        agente = criar_analista_fisico(llm=llm_falso)

        assert "basis" in agente.goal.lower()
        assert "tendência" in agente.goal.lower()

    def test_backstory_usa_jargao_do_dominio(self, llm_falso: LLMFalso):
        agente = criar_analista_fisico(llm=llm_falso)

        for termo in ("arroba", "pluma", "basis"):
            assert termo in agente.backstory.lower()

    def test_nao_permite_delegacao(self, llm_falso: LLMFalso):
        agente = criar_analista_fisico(llm=llm_falso)

        assert agente.allow_delegation is False

    def test_llm_e_repassando_por_injecao(self, llm_falso: LLMFalso):
        agente = criar_analista_fisico(llm=llm_falso)

        assert agente.llm is not None
