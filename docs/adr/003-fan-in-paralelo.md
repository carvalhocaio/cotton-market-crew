# ADR-003: Fan-in paralelo e separação entre conteúdo e orquestração de Task

## Status

Aceito

## Contexto

O Bloco 3 precisava provar dois pontos do roadmap: que múltiplos analistas
podem rodar em paralelo (`async_execution=True`) e ser consolidados por
`context=[...]`, e que esse paralelismo produz ganho de wall-clock
mensurável, não só teórico.

O escopo original do roadmap previa um terceiro analista de
logística/clima, mas o Bloco 1 nunca criou essa fonte de dados. Optamos
por ajustar o escopo: 3 analistas regionais (MT, BA, GO) do mesmo tipo
(físico) + 1 analista de mercado externo (futuro ICE + câmbio), 4 tasks
em paralelo consolidadas por 1 estrategista. Logística/clima fica anotado
como extensão futura do roadmap, não implementada aqui.

## Decisão

**`async_execution` é setado em `pipeline.py`, não nas fábricas de
`tasks.py`.** As fábricas (`criar_task_analise_fisico`,
`criar_task_analise_mercado_externo`, `criar_task_consolidacao`)
continuam descrevendo só o conteúdo da task — prompt e schema de saída.
Quem decide *como* ela é agendada (síncrona ou assíncrona) é quem monta
o pipeline. Essa separação evitou reabrir e reescrever os testes de
`tasks.py` que já estavam fechados quando o Bloco 3 mudou de escopo.

**3 instâncias separadas do agente físico**, uma por região, em vez de
1 agente reaproveitado em 3 tasks assíncronas — elimina qualquer dúvida
sobre estado compartilhado entre execuções concorrentes do mesmo `Agent`,
a custo desprezível (é só um objeto Pydantic leve).

## Achado do experimento (2026-08-03, gemini/gemini-2.5-flash)

`experimentos/medir_paralelismo.py`, rodada única por condição:

- **Wall-clock**: paralela em 18.32s, sequencial em 40.97s — ~2.24x mais
  rápida. Direcionalmente confirma a hipótese do fan-in.
- **Achado não previsto**: `successful_requests` foi 25 na paralela e 50
  na sequencial, para as mesmas 5 tasks — consistente com retry de
  formatação do `output_pydantic` (mesmo padrão observado no experimento
  de backstory do ADR-002, aqui em escala maior).
- **Limitação**: como as duas condições tiveram volumes de retry
  diferentes, parte do ganho medido de wall-clock pode ser efeito de
  "menos retry na paralela" e não puramente de concorrência. n=1 por
  condição — não dá para separar os dois efeitos com esta rodada. O
  número de 2.24x é real, mas não deve ser citado como "o paralelismo
  economiza X%" sem essa ressalva.

Decisão consciente de não investigar a fundo agora: o Bloco 5 adiciona
guardrails com sua própria camada de retry sobre esse mesmo esquema de
saída. Faz mais sentido reexaminar o padrão de retry depois que essa
camada existir, com visibilidade completa do que está causando as
chamadas extras.

## Consequências

**Positivas**

- Pipeline testado estruturalmente (74 testes) sem custo de API — só o
  experimento de medição gastou quota real.
- Separação conteúdo/orquestração em `tasks.py` vs `pipeline.py` deixou o
  ajuste de escopo (3 regiões + externo, sem logística/clima) barato de
  fazer sem retrabalho.
- Ganho de paralelismo é real e mensurável, mesmo com a ressalva.

**Negativas / trade-offs**

- A causa exata do retry alto (25-50 chamadas para 5 tasks) não foi
  investigada — fica como item em aberto para revisitar no Bloco 5.
- O número "2.24x mais rápido" não tem significância estatística (n=1,
  confundido por retry desigual) e não deve ser citado fora deste ADR
  sem a ressalva completa.