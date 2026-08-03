"""Fábricas de agentes CrewAI da mesa de comercialização de algodão.

O `llm` é sempre recebido por injeção - nunca resolvido aqui dentro. Isso
mantém as fábricas testáveis sem credencial real: o teste verifica a forma
do agente (role, goal, backstory, permissões), não o comportamento do
modelo por trás.
"""

from crewai import Agent


def criar_analista_fisico(llm: object) -> Agent:
    """Cria o agente responsável por interpretar o mercado físico regional."""
    return Agent(
        role="Analista de Mercado Físico de Algodão",
        goal=(
            "Avaliar o basis regional e apontar a tendência de curto prazo "
            "do mercado físico de algodão a partir dos indicadores "
            "disponíveis."
        ),
        backstory=(
            "Você acompanha o mercado físico de algodão brasileiro há anos, "
            "lendo o comportamento da arroba em praças como Mato Grosso, "
            "Bahia e Goiás. Sabe interpretar o basis regional frente ao  "
            "futuro e reconhece como a disponibilidade de pluma pressiona "
            "o preço físico em cada praça."
        ),
        allow_delegation=False,
        llm=llm,
    )


def criar_analista_mercado_externo(llm: object) -> Agent:
    """Cria o agente responsável pelo futuro ICE e pelo câmbio PTAX."""
    return Agent(
        role="Analista de Mercado Externo de Algodão",
        goal=(
            "Avaliar a tendência do contrato futuro na ICE e o impacto do "
            "câmbio (PTAX) sobre a competitividade do algodão brasileiro "
            "no mercado internacional."
        ),
        backstory=(
            "Você acompanha o pregão da ICE Futures US diariamente, lendo "
            "o comportamento do contrato de algodão nº 2 e sua relação com "
            "o câmbio PTAX. Sabe como a valorização ou desvalorização do "
            "real frente ao dólar altera a competitividade do algodão "
            "brasileiro exportado, mesmo quando o contrato futuro em si "
            "não se move."
        ),
        allow_delegation=False,
        llm=llm,
    )


def criar_estrategista(llm: object) -> Agent:
    """Cria o agente responsável por consolidar as análises no boletim."""
    return Agent(
        role="Estrategista da Mesa de Comercialização",
        goal=(
            "Consolidar as análises de mercado físico e mercado externo em "
            "uma leitura de risco única para o boletim semanal."
        ),
        backstory=(
            "Você lidera a mesa de comercialização e é responsável pelo "
            "boletim semanal que orienta a equipe comercial. Sabe ponderar "
            "sinais às vezes conflitantes entre o físico regional e o "
            "mercado externo, priorizando clareza sobre o risco de curto "
            "prazo em vez de previsões categóricas."
        ),
        allow_delegation=False,
        llm=llm,
    )
