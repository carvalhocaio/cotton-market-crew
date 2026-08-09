"""Testes de integração que fazem chamadas reais de LLM.

Marcados com @pytest.mark.llm — não rodam por padrão (`addopts = -m "not
llm"` em pyproject.toml). Rodar explicitamente com `pytest -m llm`.
Consomem quota real de API; mantidos mínimos de propósito — não repetem
o pipeline completo medido nos ADRs 005 e 006 (85-105 chamadas), que é
caro demais para um teste de rotina.
"""

import os
from decimal import Decimal

import pytest
from crewai import LLM, Crew, Process

from cotton_market_crew.agentes import criar_analista_fisico
from cotton_market_crew.guardrails import criar_guardrail_basis_numerico
from cotton_market_crew.store import MercadoStore
from cotton_market_crew.tasks import criar_task_analise_fisico

ORCAMENTO_MAXIMO_REQUESTS = 10

pytestmark = pytest.mark.llm

requer_gemini = pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY não configurada",
)


@requer_gemini
def test_analista_fisico_respeita_guardrail_numerico_com_llm_real():
    """Smoke test mínimo: 1 agente real, 1 task real, guardrail real.

    Cobre a mesma garantia verificada manualmente no experimento do
    Bloco 4 (ver ADR-004) — mas como teste automatizado e opcional, não
    como script solto que exige colar output à mão.
    """
    llm = LLM(
        model="gemini/gemini-2.5-flash",
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0.2,
    )
    store = MercadoStore()
    regiao = "MT"

    agente = criar_analista_fisico(llm)
    indicador = store.ultimo_indicador(regiao)
    cotacao = store.ultima_cotacao_futura()
    cambio = store.ultimo_cambio()
    basis_esperado = store.calcular_basis(regiao).valor_cents_por_libra

    task = criar_task_analise_fisico(agente, indicador, cotacao, cambio)
    task.guardrail = criar_guardrail_basis_numerico(basis_esperado)

    crew = Crew(agents=[agente], tasks=[task], process=Process.sequential)
    resultado = crew.kickoff()

    assert resultado.pydantic.regiao == regiao
    assert Decimal(str(resultado.pydantic.basis_cents_lb)) == basis_esperado
    assert crew.usage_metrics.successful_requests <= ORCAMENTO_MAXIMO_REQUESTS
