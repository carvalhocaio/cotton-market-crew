# ADR-005: Guardrails determinísticos e o custo real da validação

## Status

Aceito

## Contexto

O Bloco 5 precisava adicionar duas camadas de proteção sobre a saída dos
agentes: uma checagem numérica (o basis reportado bate com o que o
`MercadoStore` calcula de forma independente?) e uma checagem de
compliance (o comentário estratégico não usa linguagem de recomendação
ou garantia?). O objetivo declarado desde o ADR-001 era "o LLM redige, o
Python garante" — mesmo princípio do `cotton-claims-agent`, agora via
`Task(guardrail=...)` nativo do CrewAI em vez de lógica manual.

## Decisão

**Guardrail numérico como fábrica com closure.**
`criar_guardrail_basis_numerico(basis_esperado)` fecha sobre o valor
calculado pelo `MercadoStore` (fonte de verdade independente da saída do
LLM) e devolve um `Callable[[TaskOutput], tuple[bool, Any]]` — a
assinatura que o CrewAI exige recebe só a saída, então o valor de
referência precisa vir por closure. Tolerância de 0.05 cents/lb para
absorver arredondamento.

**Guardrail de compliance bloqueia frases, não palavras soltas.**
`"venda"` isolada é vocabulário legítimo do domínio
(`Cambio.ptax_venda`); bloquear a palavra geraria falso positivo em texto
de mercado normal. A lista (`FRASES_PROIBIDAS`) cobre frases de
recomendação e garantia. Limitação conhecida e aceita: um LLM pode
driblar reformulando a recomendação de um jeito não coberto pela lista —
isso é fricção adicional, não uma garantia formal.

**Escopo reduzido em relação ao plano original.** Disclaimer e
data-base do boletim não passam por guardrail: são texto determinístico
que o Python vai anexar diretamente no template final (Bloco 6), sem
nunca passar pelo LLM. Guardrail existe para validar algo que o LLM pode
errar; não há o que validar em um rodapé fixo. A task de mercado externo
também ficou sem guardrail — sua saída (`Literal` + comentário) não tem
um valor numérico contínuo comparável contra o `MercadoStore`.

## Achado da execução ponta a ponta (2026-08-03, gemini/gemini-2.5-flash)

`experimentos/rodar_pipeline_completo.py`, execução única da Crew
completa (5 tasks, guardrails ativos):

- **Correção validada**: os três basis regionais que chegaram ao boletim
  final batem exatamente com `MercadoStore.calcular_basis` (MT=14.27,
  BA=11.30, GO=14.51), e o basis médio do estrategista (13.36) é a média
  exata dos três — evidência de que os números sobreviventes ao guardrail
  são de fato corretos, não só "aceitos por acaso".
- **Guardrail rejeitou saída malformada em ato**: logs mostram bloqueios
  reais (`"Saída sem output_pydantic"`) forçando reexecução — não é só
  estrutura testada, é comportamento observado em produção simulada.
- **Custo real do bloco**: 85 `successful_requests` para 5 tasks, contra
  25 no mesmo pipeline sem tool nem guardrail (experimento do Bloco 3) —
  aproximadamente 3.4x mais caro. Confirma a preocupação registrada no
  ADR-003 sobre custo composto de camadas de retry.
- **Resiliência de provider observada, não nossa**: 2 ocorrências de
  resposta vazia da API, com retry automático do próprio CrewAI —
  categoria de falha diferente de guardrail rejeitando conteúdo.
- **Limitação**: n=1 de execução completa. O multiplicador de 3.4x é um
  dado único, não uma média confiável — mas é grande o suficiente para
  já justificar preocupação de custo em uso real recorrente (boletim
  semanal).

## Consequências

**Positivas**

- Primeira prova de guardrail funcionando em execução real, não só
  testado com `TaskOutput` construído manualmente.
- Trilha de decisão completa desde o ADR-001 até aqui: função pura →
  tool → task redesenhada para forçar uso da tool → guardrail validando
  o resultado contra a mesma fonte de verdade usada desde o início.

**Negativas / trade-offs**

- Custo ~3.4x maior que o pipeline sem proteção é um número real que
  precisa entrar na conversa sobre viabilidade de rodar isso
  semanalmente em produção — vale revisitar ao decidir sobre o processo
  hierárquico do Bloco 6, que provavelmente adiciona custo por cima
  deste.
- Guardrail de compliance é fricção por lista de frases, não garantia
  formal — um adversário deliberado (ou um LLM criativo) pode
  contornar.
- Logs de guardrail sem nome descritivo (`"Guardrail  blocked"`) —
  cosmético, não bloqueante, mas prejudica observabilidade em produção.
