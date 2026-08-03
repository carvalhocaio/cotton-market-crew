from crewai import Agent

from cotton_market_crew.agentes import criar_analista_fisico


class TestCriarAnalistaFisico:
    def test_retorna_instancia_de_agent(self, llm_falso):
        agente = criar_analista_fisico(llm=llm_falso)

        assert isinstance(agente, Agent)

    def test_role_reflete_o_dominio(self, llm_falso):
        agente = criar_analista_fisico(llm=llm_falso)

        assert "físico" in agente.role.lower()
        assert "algodão" in agente.role.lower()

    def test_goal_menciona_basis_e_tendencia(self, llm_falso):
        agente = criar_analista_fisico(llm=llm_falso)

        assert "basis" in agente.goal.lower()
        assert "tendência" in agente.goal.lower()

    def test_backstory_usa_jargao_do_dominio(self, llm_falso):
        agente = criar_analista_fisico(llm=llm_falso)

        for termo in ("arroba", "pluma", "basis"):
            assert termo in agente.backstory.lower()

    def test_nao_permite_delegacao(self, llm_falso):
        agente = criar_analista_fisico(llm=llm_falso)

        assert agente.allow_delegation is False

    def test_llm_e_repassado_por_injecao(self, llm_falso):
        agente = criar_analista_fisico(llm=llm_falso)

        assert agente.llm is llm_falso