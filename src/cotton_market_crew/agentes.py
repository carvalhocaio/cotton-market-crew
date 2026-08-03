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
