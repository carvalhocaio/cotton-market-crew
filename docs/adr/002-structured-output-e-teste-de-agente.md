# ADR-002: Structured output e teste de agentes sem custo de API

## Status

Aceito

## Contexto

O Bloco 2 introduziu o primeiro agente CrewAI real (analista de mercado
físico) e precisava resolver dois problemas: como garantir que a saída do
LLM seja consumível por código (não texto livre), e como testar a forma
do agente/task sem gastar quota de API a cada `pytest`.

## Decisão

**Structured output via `Task(output_pydantic=...)`.** `AnaliseFisico`
(em `esquemas.py`) usa `Literal` para região e tendência — restringindo o
espaço de resposta na própria assinatura de tipo, não só em validação
posterior — e `ConfigDict(extra="forbid")`, que rejeita qualquer campo que
o LLM inventar além do schema.

**Injeção de LLM nos agentes.** `criar_analista_fisico(llm: object)`
nunca resolve credencial internamente — quem chama decide qual LLM entra.
Isso pareceu óbvio até esbarrar num problema real: passar uma string
qualquer (`"modelo-de-teste"`) faz o CrewAI tentar resolver um provider de
verdade via litellm, e falhar pedindo `OPENAI_API_KEY` mesmo numa string
que não corresponde a nenhum provider intencional.

A saída foi criar um duplo de teste de verdade: uma subclasse mínima de
`crewai.llm.BaseLLM` (só o método `call` é abstrato), sem nenhuma chamada
de rede. Isso virou a fixture `llm_falso` em `tests/conftest.py`,
reaproveitada por `test_agentes.py` e `test_tasks.py`.

## Consequências

**Positivas**

- Suíte inteira (agentes + tasks) roda em milissegundos, sem chave de API,
  sem rede.
- O padrão do duplo de `BaseLLM` é reaproveitável em qualquer projeto
  CrewAI futuro — vale levar para o Bloco 7 como fixture central de teste.

**Negativas / trade-offs**

- Os testes cobrem *forma* (role, goal, output_pydantic, allow_delegation),
  não *comportamento* do modelo. Nenhum teste automatizado garante que o
  LLM de verdade preenche `AnaliseFisico` corretamente ou respeita o
  jargão do backstory — isso só se verifica com execução real,
  intencionalmente fora do `make check`.
- A pergunta original do roadmap ("o jargão no backstory muda a saída de
  verdade?") continua em aberto — decidir se/quando rodar esse experimento.

## Achado do experimento (2026-08-03, gemini/gemini-2.5-flash)

Rodada única por agente, mesma Task, `temperature=0.2`:

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
  estatística, é um dado exploratório único. Backstory calibrado
  parece reduzir fricção de formatação mais do que mudar a análise em si
  — mas isso precisaria de repetição para virar afirmação confiável.