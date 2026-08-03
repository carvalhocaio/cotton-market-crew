# ADR-004: Ferramenta de conversão e redesenho da Task física

## Status

Aceito

## Contexto

O Bloco 1 isolou `arroba_reais_para_cents_libra` como função pura,
deixando registrado no ADR-001 que ela viraria uma tool do CrewAI no
Bloco 4. Simplesmente anexar a tool ao agente sem mudar mais nada não
seria suficiente: até este ponto, `criar_task_analise_fisico` recebia um
`Basis` já calculado pelo `MercadoStore` e entregava o número pronto no
prompt — o agente nunca teria motivo real para chamar a ferramenta.

## Decisão

**A tool é uma casca fina sobre a função pura.** `ferramentas.py` expõe
`converter_arroba_para_cents_libra_tool` via `@tool` do CrewAI, chamando
`arroba_reais_para_cents_libra` internamente. Não duplica lógica — só
adapta o formato de saída (string, para o LLM ler) e captura
`ConversaoInvalidaError` para devolver como texto de erro em vez de
deixar a exceção estourar, para que o agente veja o problema e possa
reagir em vez do processo quebrar.

**A Task física foi redesenhada para forçar o uso da ferramenta.**
`criar_task_analise_fisico` passa a receber `Cambio` (PTAX bruto) em vez
de `Basis` (já calculado). O prompt entrega o indicador físico em
R$/arroba e o futuro em cents/lb — unidades diferentes, não comparáveis
diretamente — e instrui o agente a converter usando a ferramenta antes de
calcular o basis. `MercadoStore.calcular_basis` continua existindo,
intocado, como fonte de verdade independente para comparação (ver
experimento abaixo e uso futuro no guardrail do Bloco 5).

Essa mudança tocou três arquivos já fechados (`tasks.py`, `test_tasks.py`,
`pipeline.py`). Decisão consciente de reabri-los: sem isso, o Bloco 4
seria estrutural (a tool existe, os testes passam) mas vazio na prática
(nunca seria chamada de verdade).

## Achado do experimento (2026-08-03, gemini/gemini-2.5-flash)

`experimentos/verificar_uso_da_ferramenta.py`, execução única:

- **Basis calculado pelo Python** (`MercadoStore.calcular_basis`, MT):
  14.27 cents/lb.
- **Basis reportado pelo agente**: 14.27 cents/lb. Diferença: 0.0000.
- Precisão exata de centavos é evidência forte de uso real da ferramenta
  — LLM não acerta essa conta de cabeça com essa precisão de forma
  confiável.
- `successful_requests=2`, mas diferente do padrão de retry visto nos
  ADRs 002 e 003: aqui é o fluxo saudável de tool-calling (1 chamada para
  decidir usar a ferramenta, 1 chamada para formatar a resposta final com
  o resultado) — não uma falha de formatação sendo corrigida.

## Consequências

**Positivas**

- Primeira prova empírica direta (não só estrutural) de que uma tool
  CrewAI é efetivamente usada pelo agente, com evidência numérica exata
  em vez de inferência sobre o texto da resposta.
- O padrão de comparação `MercadoStore` vs. saída do agente é reaproveitável
  como esqueleto do guardrail numérico do Bloco 5.
- `conversao.py` permanece uma única fonte de verdade para a fórmula —
  usada por `MercadoStore.calcular_basis` (Python puro) e pela tool
  (LLM), sem duplicação.

**Negativas / trade-offs**

- n=1 novamente. Uma coincidência de precisão em uma única rodada não é
  garantia de comportamento consistente — o guardrail do Bloco 5 existe
  justamente para não depender dessa confiança.
- O redesenho da Task quebrou testes que já estavam fechados,
  reforçando que "fechado" em um projeto de agentes é relativo: uma
  mudança de estratégia de prompt pode exigir revisão de decisões
  anteriores mesmo com testes verdes.