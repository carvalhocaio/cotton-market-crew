# ADR-001: Fundação determinística antes de agentes

## Status

Aceito

## Contexto

O objetivo final do projeto é um crew CrewAI que gera um boletim semanal de
mercado de algodão. Antes de introduzir qualquer LLM, o pipeline precisa de
uma base de fatos estável: modelos de domínio validados e uma fonte de dados
que não varie entre execuções.

Duas alternativas foram consideradas para a fonte de dados:

1. Integrar diretamente com APIs reais (CEPEA, ICE, PTAX/BACEN) desde o início.
2. Construir um store local com dados sintéticos plausíveis, versionando no repositório.

## Decisão

O `MercadoStore` lê três CSVs versionados
(`dados/indicador_fisico.csv`, `dados/cotacao_futura.csv`,
`dados/cambio.csv`) contendo uma série sintética de 10 dias úteis para MT,
BA e GO. Os valores foram gerados com seed fixa e não representam cotações
reais de mercado - servem para exercitar o pipeline, não para uso
comercial.

Os fatos de mercado são modelados como `dataclass(frozen=True, slots=True)`
com validação em `__post_init__`: se o objeto foi construído, ele é válido.
Erros de domínio têm hierarquia própria (`MercadoAlgodaoError` →
`IndicadorInvalidoError`, `CotacaoInvalidaError`, `BasisInvalidoError`).

A conversão R$/arroba → cents/lb foi isolada em `conversao.py` como função
pura, independente do store e do domínio de agentes. Essa separação importa
porque essa função será reaproveitada como tool do CrewAI no Bloco 4 - o
agente decide quando chamar a conversão, mas o cálculo em si nunca passa
pelo LLM.

### Trade-off assumido: `calcular_basis` não casa datas entre séries

`MercadoStore.calcular_basis` usa o último indicador físico, a última
cotação futura e o último câmbio de forma **independente** — não exige que
as três venham da mesma data. Nos dados sintéticos isso não aparece porque
as três séries terminam no mesmo dia, mas numa fonte real (CEPEA, ICE,
PTAX/BACEN publicam em horários e calendários diferentes) isso pode juntar
dados defasados de um dia ou mais.

Decisão consciente de não resolver isso agora: forçar coincidência de data
exigiria decisão de negócio (tolerar quantos dias de defasagem? usar o
último valor disponível de cada série mesmo que desatualizado? bloquear o
cálculo?) que não faz sentido tomar sobre dados sintéticos. Revisitar
quando o store trocar para fonte ao vivo.

## Consequências

**Positivas**

- Testes determinísticos: o mesmo boletim sai hoje ou daqui a um mês, sem
  depender de rede.
- Nenhuma quota de API é consumida nos Blocos 1–3, que são justamente onde
  mais se itera.
- Trocar a fonte por uma API real no futuro é uma mudança isolada nos
  métodos `_carregar_*` do `MercadoStore` — o resto do domínio (dataclasses,
  conversão, cálculo de basis) não muda.

**Negativas / trade-offs**

- Os dados não refletem o mercado real; qualquer leitura do boletim como
  informação de mercado seria enganosa. Isso precisa ficar explícito em
  qualquer saída gerada (guardrail de compliance no Bloco 5).
- `calcular_basis` pode juntar indicador, futuro e câmbio de datas
  diferentes quando a fonte for ao vivo — ver seção de trade-off acima.
- Uma migração futura para dados ao vivo exigirá tratar casos que o CSV
  sintético não força a considerar: linhas ausentes, atrasos de publicação,
  fuso horário do fechamento do pregão.
