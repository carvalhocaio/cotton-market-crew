# Cotton Market Crew

Boletim semanal de mercado de algodão gerado por uma crew de agentes
[CrewAI](https://docs.crewai.com/), com dados sintéticos (mas
estruturalmente realistas) e validação determinística sobre tudo que o
LLM produz.

O princípio central do projeto, presente desde o [ADR-001](docs/adr/001-fundacao-deterministica.md):
**o LLM redige, o Python garante.** Fatos de mercado, conversões
numéricas, disclaimer e data-base nunca são gerados pelo modelo — só a
interpretação (tendência, comentário estratégico) passa pelo LLM, e
mesmo essa é validada por guardrails determinísticos antes de compor o
boletim final.

## Como funciona

1. **`MercadoStore`** ([`store.py`](src/cotton_market_crew/store.py)) lê
   indicador físico, cotação futura (ICE #2) e câmbio PTAX de CSVs
   versionados em [`dados/`](dados/) — nada de API ao vivo, o boletim é
   100% reproduzível.
2. Quatro agentes analisam o mercado em paralelo (`async_execution`):
   três **analistas de mercado físico** (um por região — MT, BA, GO) e um
   **analista de mercado externo** (futuro ICE + câmbio). Os analistas
   físicos recebem os dados brutos (R$/arroba, PTAX) e precisam converter
   para cents/lb usando uma tool antes de calcular o basis — nunca de
   cabeça.
3. Um **estrategista** consolida as quatro análises em uma leitura de
   risco única, via `context` do CrewAI (fan-in).
4. **Guardrails** (`Task(guardrail=...)`) rejeitam saídas que divirjam do
   basis calculado independentemente pelo `MercadoStore`, ou que usem
   linguagem de recomendação de compra/venda.
5. **`renderizar_boletim`** ([`boletim.py`](src/cotton_market_crew/boletim.py))
   monta o markdown final, anexando data-base e disclaimer fixo — texto
   que nunca passa pelo LLM.

Dois pipelines estão disponíveis em [`pipeline.py`](src/cotton_market_crew/pipeline.py):

- `montar_pipeline` — sequencial, com os quatro analistas em paralelo e
  fan-in no estrategista (usado por padrão em `main.py`).
- `montar_pipeline_hierarquico` — `Process.hierarchical`, com o
  estrategista como `manager_agent` decidindo a quem delegar. Mantido
  para comparação; ver [ADR-006](docs/adr/006-processo-hierarquico.md)
  sobre por que o ganho é questionável neste desenho.

## Requisitos

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)
- Uma `GEMINI_API_KEY` válida (só para rodar o pipeline de verdade ou os
  testes marcados `llm`; a suíte padrão não faz chamadas reais)

## Instalação

```bash
uv sync
```

## Uso

```bash
export GEMINI_API_KEY="sua-chave-aqui"
uv run python main.py
```

Isso roda o pipeline sequencial completo (~85 chamadas de LLM, ver
[ADR-005](docs/adr/005-guardrails-determinísticos.md)) e imprime o
boletim final, seguido do uso de tokens da crew.

## Testes

A suíte inteira roda sem chamadas reais de LLM por padrão — agentes e
tasks são testados na forma (role, goal, schema de saída), não no
comportamento do modelo (ver [ADR-002](docs/adr/002-structured-output-e-teste-de-agente.md)
e [ADR-007](docs/adr/007-testes-sem-custo-de-api.md)).

```bash
uv run pytest
```

Para incluir os testes que fazem chamadas reais (marcados `llm`, exigem
`GEMINI_API_KEY`):

```bash
uv run pytest -m llm
```

## Lint e formatação

```bash
make lint          # ruff check
make lint-fix       # ruff check --fix
make format          # ruff format
make format-check    # ruff format --check
make check          # lint + format-check
```

## Estrutura

```
src/cotton_market_crew/
├── dominio.py       # Value objects imutáveis (IndicadorFisico, CotacaoFutura, Cambio, Basis)
├── conversao.py     # Função pura de conversão R$/arroba -> cents/lb
├── store.py         # MercadoStore: leitura determinística dos CSVs de dados/
├── esquemas.py       # Schemas Pydantic da fronteira LLM -> domínio (output_pydantic)
├── ferramentas.py     # Tools do CrewAI (casca fina sobre conversao.py)
├── agentes.py        # Fábricas dos agentes CrewAI (analistas + estrategista)
├── tasks.py          # Fábricas das Tasks (prompt + schema de saída)
├── guardrails.py     # Validações determinísticas sobre a saída dos agentes
├── boletim.py        # Renderização determinística do boletim final
└── pipeline.py        # Monta as Crews (sequencial e hierárquica)

dados/                # CSVs versionados: indicador físico, cotação futura, câmbio
docs/adr/            # Architecture Decision Records, um por bloco do roadmap
experimentos/         # Scripts exploratórios (medição de paralelismo, comparação de processos, etc.)
tests/                # Suíte pytest (lógica isolada de LLM por padrão)
main.py               # Ponto de entrada: gera e imprime o boletim semanal
```

## Decisões de arquitetura

O histórico completo de decisões está em [`docs/adr/`](docs/adr/):

- [ADR-001](docs/adr/001-fundacao-deterministica.md) — Fundação determinística antes de agentes
- [ADR-002](docs/adr/002-structured-output-e-teste-de-agente.md) — Structured output e teste de agentes sem custo de API
- [ADR-003](docs/adr/003-fan-in-paralelo.md) — Fan-in paralelo e separação entre conteúdo e orquestração de Task
- [ADR-004](docs/adr/004-ferramenta-de-conversao-e-redesenho-da-task.md) — Ferramenta de conversão e redesenho da Task física
- [ADR-005](docs/adr/005-guardrails-determinísticos.md) — Guardrails determinísticos e o custo real da validação
- [ADR-006](docs/adr/006-processo-hierarquico.md) — Processo hierárquico: custo medido, valor questionável neste desenho
- [ADR-007](docs/adr/007-testes-sem-custo-de-api.md) — Separação formal entre testes de lógica e testes de LLM real

## Aviso

Os dados em `dados/` são sintéticos, gerados para fins de estudo. O
boletim resultante não representa cotações reais de mercado e não
constitui recomendação de comercialização — o próprio texto gerado
carrega esse disclaimer.
