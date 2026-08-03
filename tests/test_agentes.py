from crewai import Agent

from cotton_market_crew.agentes import (
    criar_analista_fisico,
    criar_analista_mercado_externo,
    criar_estrategista,
)


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

    def test_tem_a_ferramenta_de_conversao(self, llm_falso):
        from cotton_market_crew.ferramentas import (
            converter_arroba_para_cents_libra_tool,
        )

        agente = criar_analista_fisico(llm=llm_falso)

        assert converter_arroba_para_cents_libra_tool in agente.tools


class TestCriarAnalistaMercadoExterno:
    def test_retorna_instancia_de_agent(self, llm_falso):
        agente = criar_analista_mercado_externo(llm=llm_falso)

        assert isinstance(agente, Agent)

    def test_role_reflete_o_dominio(self, llm_falso):
        agente = criar_analista_mercado_externo(llm=llm_falso)

        assert "externo" in agente.role.lower()
        assert "algodão" in agente.role.lower()

    def test_goal_menciona_futuro_e_cambio(self, llm_falso):
        agente = criar_analista_mercado_externo(llm=llm_falso)

        assert "futuro" in agente.goal.lower()
        assert "câmbio" in agente.goal.lower()

    def test_backstory_usa_jargao_do_dominio(self, llm_falso):
        agente = criar_analista_mercado_externo(llm=llm_falso)

        for termo in ("ice", "ptax", "contrato"):
            assert termo in agente.backstory.lower()

    def test_nao_permite_delegacao(self, llm_falso):
        agente = criar_analista_mercado_externo(llm=llm_falso)

        assert agente.allow_delegation is False


class TestCriarEstrategista:
    def test_retorna_instancia_de_agent(self, llm_falso):
        agente = criar_estrategista(llm=llm_falso)

        assert isinstance(agente, Agent)

    def test_role_reflete_consolidacao(self, llm_falso):
        agente = criar_estrategista(llm=llm_falso)

        assert "estrategista" in agente.role.lower()

    def test_goal_menciona_consolidacao_e_risco(self, llm_falso):
        agente = criar_estrategista(llm=llm_falso)

        assert "consolidar" in agente.goal.lower()
        assert "risco" in agente.goal.lower()

    def test_backstory_usa_jargao_da_mesa(self, llm_falso):
        agente = criar_estrategista(llm=llm_falso)

        assert "boletim" in agente.backstory.lower()

    def test_nao_permite_delegacao(self, llm_falso):
        agente = criar_estrategista(llm=llm_falso)

        assert agente.allow_delegation is False
