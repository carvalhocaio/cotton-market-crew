# ADR-002: Structured output, teste de agentes sem custo de API e o experimento de backstory

## Status

Aceito

## Contexto

O Bloco 2 introduziu o primeiro agente CrewAI real (analista de mercado
físico) e precisava resolver três problemas: garantir que a saída do LLM
seja consumível por código (não texto livre), testar a forma do
agente/task sem gastar quota de API a cada `pytest`, e verificar
empiricamente se um backstory calibrado com jargão do domínio muda a
saída de fato, ou é só estética.

## Decisão

**Structured output via `Task(output_pydantic=...)`.** `AnaliseFisico`
(em `esquemas.py`) usa `Literal` para região e tendência — restringindo o
espaço de resposta na própria assinatura de tipo — e
`ConfigDict(extra="forbid")`, que rejeita qualquer campo que o LLM
inventar além do schema.

**Injeção de LLM nos agentes.** `criar_analista_fisico(llm: object)` nunca
resolve credencial internamente. Isso esbarrou num problema real: passar
uma string qualquer (`"modelo-de-teste"`) faz o CrewAI tentar resolver um
provider de verdade via litellm e falhar pedindo `OPENAI_API_KEY`. A saída
foi um duplo de teste de verdade — subclasse mínima de
`crewai.llm.BaseLLM` (só `call` é abstrato) — virando a fixture
`llm_falso` em `tests/conftest.py`, reaproveitada por `test_agentes.py` e
`test_tasks.py`.

**Experimento de backstory (`experimentos/comparar_backstory.py`).** Não é
testável com TDD tradicional — saída de LLM não é determinística. É um
script de rodada única, fora de `make check`, comparado manualmente.

## Achado do experimento (2026-08-03, gemini/gemini-2.5-flash)

Rodada única por agente, mesma `Task`, `temperature=0.2`:

- **Conteúdo**: tendência e argumento do comentário saíram equivalentes
  entre o agente calibrado (jargão no backstory) e o agente de controle
  (backstory genérico em inglês). O jargão técnico usado pelo agente
  genérico veio da própria `Task.description` (fatos injetados), não do
  backstory — sugerindo que o que mais influencia terminologia correta é
  o conteúdo da task, não necessariamente o backstory do agente.
- **Custo**: o agente calibrado fechou em 1 chamada (856 tokens); o
  genérico precisou de 2 (1656 tokens) — consistente com um retry de
  `output_pydantic` por falha de formato na primeira tentativa.
- **Limitação**: n=1 por agente, temperatura não-zero. Não é evidência
  estatística, é um dado exploratório único. Backstory calibrado parece
  reduzir fricção de formatação mais do que mudar a análise em si — mas
  confirmar isso exigiria repetição, o que não foi feito neste ADR.

## Consequências

**Positivas**

- Suíte de testes (agentes + tasks) roda em milissegundos, sem chave de
  API, sem rede.
- O padrão do duplo de `BaseLLM` é reaproveitável em qualquer projeto
  CrewAI futuro.
- Registro honesto de que o efeito do backstory pode estar mais em
  formatação/custo do que em qualidade de análise — evita achismo no
  próximo projeto CrewAI.

**Negativas / trade-offs**

- Os testes automatizados cobrem *forma* (role, goal, output_pydantic,
  allow_delegation), não *comportamento* do modelo real.
- A pergunta "backstory calibrado reduz retry de formato de verdade?"
  continua em aberto estatisticamente — só há uma amostra.