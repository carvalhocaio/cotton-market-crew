# ADR-006: Processo hierárquico — custo medido, valor questionável neste desenho

## Status

Aceito

## Contexto

O roadmap original apostava que `Process.hierarchical` custaria 2-3x mais
que o sequencial e entregaria pouco. O Bloco 6 precisava transformar essa
aposta em número real, comparando contra a referência já medida no
ADR-005 (85 `successful_requests` para o pipeline sequencial com
guardrails).

## Decisão

**`montar_pipeline_hierarquico` reaproveita `_montar_analistas_e_tasks_upstream`**,
extraído por refactor DRY do `montar_pipeline` original — os 4 analistas
e seus guardrails numéricos são idênticos entre os dois pipelines; só
muda como a `Crew` é montada.

**O estrategista vira `manager_agent`**, não um agente regular do crew —
restrição do CrewAI: o gerente não pode aparecer em `agents` nem ter
`tools`. Como `criar_estrategista` nunca teve ferramentas, essa
restrição foi satisfeita sem esforço extra.

**Tasks upstream ficam síncronas no hierárquico** (`async_execution` não
é setado, fica `False` por default) — decisão deliberada para isolar a
variável sob teste (tipo de processo) da variável já medida no Bloco 3
(paralelismo). Consequência aceita: wall-clock entre os dois pipelines
não é comparável.

## Achado do experimento (2026-08-03, gemini/gemini-2.5-flash)

`experimentos/comparar_hierarquico_vs_sequencial.py`, execução única:

- **Custo**: 105 `successful_requests` no hierárquico vs. 85 no
  sequencial (ADR-005) — **+23.5%**. Confirma a direção da aposta
  original, mas bem abaixo do "2-3x" previsto.
- **Achado que reenquadra o resultado**: o `manager_agent` não tem
  ferramentas, então a delegação observada não foi "escolha inteligente
  do gerente" — foi estruturalmente forçada, já que ele não conseguiria
  fazer a conversão arroba→cents/lb sozinho de nenhum jeito. Este
  experimento mediu o custo do *mecanismo* de delegação, não o valor de
  um gerente decidindo entre executar e delegar.
- **Delegação funcionou corretamente**: logs de "Repaired JSON" mostram
  a tool interna de delegação chamando o co-worker pelo role exato
  (`"Analista de Mercado Externo de Algodão"`), com resposta bem
  formada no schema esperado.
- **Correção idêntica ao sequencial**: `basis_medio_cents_lb=13.36`,
  mesmo valor exato do ADR-005 — esperado (o guardrail garante a mesma
  correção nos dois pipelines), não evidência de qualidade superior.
- **Mesmos sintomas de instabilidade do Bloco 5** reapareceram (retries
  de `output_pydantic` vazio, respostas vazias da API) — sugere que são
  característica do modelo/schema, não artefato do tipo de processo.
- **Limitação**: n=1, wall-clock não comparável (ver decisão acima). O
  +23.5% é um dado único, não uma média confiável.

## Consequências

**Positivas**

- Aposta inicial do roadmap validada com número real, não intuição.
- Mecanismo de delegação por role confirmado funcional via log direto.
- Refactor DRY (`_montar_analistas_e_tasks_upstream`) deixou os dois
  pipelines de fácil manutenção conjunta.

**Negativas / trade-offs**

- O experimento não testa a pergunta mais interessante — "um gerente com
  julgamento real (e talvez suas próprias ferramentas) toma decisões
  melhores de delegação que compensam o custo?" — porque o gerente deste
  desenho não tinha alternativa. Testar isso exigiria um manager_agent
  com mais autonomia real, o que foge do escopo deste bloco.
- Para este domínio (pipeline com estrutura já conhecida e fixa: 3
  regiões + 1 externo + 1 consolidação), `Process.sequential` com
  `async_execution` continua sendo a escolha correta — não há incerteza
  sobre "quem deveria fazer o quê" que justifique pagar a mais por um
  gerente decidir isso em tempo de execução.
