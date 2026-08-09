# ADR-007: Separação formal entre testes de lógica e testes de LLM real

## Status

Aceito

## Contexto

Desde o Bloco 2, a suíte inteira (101 testes até este ponto) já rodava
sem nenhuma chamada real de LLM — resultado do padrão `LLMFalso`
estabelecido no ADR-002. O que faltava era formalizar essa separação
como mecanismo de pytest, em vez de ser só uma convenção implícita, e
transformar os scripts exploratórios de `experimentos/` (que exigiam
rodar manualmente e colar output) num teste automatizado e opcional.

## Decisão

**Marker `llm` registrado em `pyproject.toml`**, com
`addopts = "-m 'not llm'"` — por padrão, `pytest` roda só os 101 testes
de lógica pura, sem custo. `pytest -m llm` roda explicitamente os testes
que fazem chamadas reais. `pytest -m ""` sobrepõe o `addopts` e roda
tudo, se algum dia fizer sentido.

**`tests/test_integracao_llm.py` cobre um recorte mínimo, não o pipeline
completo.** Rodar as 5 tasks (85-105 chamadas medidas nos ADRs 005 e 006)
seria caro demais para um teste que idealmente roda com alguma
frequência. O smoke test cobre 1 agente + 1 task + 1 guardrail real — a
mesma garantia verificada manualmente no experimento do Bloco 4, agora
automatizada.

**Orçamento de requests como asserção**, não só verificação de
correção. `crew.usage_metrics.successful_requests <= 10` falha o teste
se o custo por chamada disparar (mudança de modelo, prompt mais confuso),
em vez de silenciosamente custar mais caro sem ninguém notar.

**`@pytest.mark.skipif` por ausência de `GEMINI_API_KEY`** — quem rodar
`pytest -m llm` sem a chave configurada recebe skip com razão explícita,
não falha.

## Consequências

**Positivas**

- Separação de custo agora é mecanismo verificável (`pytest` puro nunca
  gasta quota), não só disciplina de quem está escrevendo os testes.
- O padrão de smoke test mínimo é reaproveitável para cobrir outros
  agentes/guardrails no futuro sem repetir o custo do pipeline completo.
- CI (se/quando existir) pode rodar a suíte inteira sem segredo de API
  configurado, e opcionalmente rodar `-m llm` como job separado com
  orçamento e frequência próprios.

**Negativas / trade-offs**

- O smoke test cobre só o agente físico com guardrail numérico — o
  guardrail de compliance e o mercado externo não têm cobertura
  equivalente com LLM real ainda. Extensão natural, não crítica agora.
- Orçamento de 10 requests é um número emprestado da observação (~2
  chamadas típicas), não uma garantia formal — um dia de instabilidade
  do provider pode estourar o teto por causas fora do nosso controle.
