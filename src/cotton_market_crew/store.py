"""Store determinístico do mercado de algodão.

Lê fatos de mercado a partir de CSVs versionados no repositório em vez de
uma API ao vivo. Isso torna o resto do pipeline (agentes, guardrails,
testes) reproduzível: o mesmo boletim sai hoje ou daqui a um mês, sem
depender de rede nem consumir quota de API externa.

Trocar por uma fonte ao vivo (CEPEA, ICE, PTAX/BACEN) no futuro significa
substituir só os métodos `_carregar_*`; o resto do domínio não muda.
"""

import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from cotton_market_crew.conversao import arroba_reais_para_cents_libra
from cotton_market_crew.dominio import Basis, Cambio, CotacaoFutura, IndicadorFisico

DIRETORIO_DADOS_PADRAO = Path(__file__).resolve().parents[2] / "dados"


class MercadoStoreError(Exception):
    """Erro ao carregar ou consultar o store de mercado."""


def _ler_csv(caminho: Path) -> list[dict[str, str]]:
    if not caminho.exists():
        raise MercadoStoreError(f"Arquivo de dados não encontrado: {caminho}")
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


class MercadoStore:
    """Acesso de leitura aos fatos de mercado carregados em memória."""

    def __init__(self, diretorio_dados: Path = DIRETORIO_DADOS_PADRAO) -> None:
        if not diretorio_dados.exists():
            raise MercadoStoreError(
                f"Diretório de dados não encontrado: {diretorio_dados}"
            )
        self._diretorio = diretorio_dados
        self._indicadores = self._carregar_indicadores()
        self._cotacoes = self._carregar_cotacoes()
        self._cambios = self._carregar_cambios()

    def _carregar_indicadores(self) -> list[IndicadorFisico]:
        linhas = _ler_csv(self._diretorio / "indicador_fisico.csv")
        return [
            IndicadorFisico(
                data=date.fromisoformat(linha["data"]),
                regiao=linha["regiao"],
                reais_por_arroba=Decimal(linha["reais_por_arroba"]),
            )
            for linha in linhas
        ]

    def _carregar_cotacoes(self) -> list[CotacaoFutura]:
        linhas = _ler_csv(self._diretorio / "cotacao_futura.csv")
        return [
            CotacaoFutura(
                data=date.fromisoformat(linha["data"]),
                contrato=linha["contrato"],
                cents_por_libra=Decimal(linha["cents_por_libra"]),
            )
            for linha in linhas
        ]

    def _carregar_cambios(self) -> list[Cambio]:
        linhas = _ler_csv(self._diretorio / "cambio.csv")
        return [
            Cambio(
                data=date.fromisoformat(linha["data"]),
                ptax_venda=Decimal(linha["ptax_venda"]),
            )
            for linha in linhas
        ]

    def listar_indicadores(
        self,
        regiao: str | None = None,
    ) -> list[IndicadorFisico]:
        if regiao is None:
            return list(self._indicadores)
        return [i for i in self._indicadores if i.regiao == regiao]

    def ultimo_indicador(self, regiao: str) -> IndicadorFisico:
        candidatos = self.listar_indicadores(regiao)
        if not candidatos:
            raise MercadoStoreError(f"Nenhum indicador para região '{regiao}'.")
        return max(candidatos, key=lambda i: i.data)

    def listar_cotacoes_futuras(self) -> list[CotacaoFutura]:
        return list(self._cotacoes)

    def ultima_cotacao_futura(self) -> CotacaoFutura:
        if not self._cotacoes:
            raise MercadoStoreError("Nenhuma cotação futura carregada.")
        return max(self._cotacoes, key=lambda c: c.data)

    def listar_cambios(self) -> list[Cambio]:
        return list(self._cambios)

    def ultimo_cambio(self) -> Cambio:
        if not self._cambios:
            raise MercadoStoreError("Nenhum câmbio carregado.")
        return max(self._cambios, key=lambda c: c.data)

    def calcular_basis(self, regiao: str) -> Basis:
        """Calcula o basis regional usando os últimos valores disponíveis.

        Basis = físico (convertido para cents/lb) - futuro (cents/lb).
        """
        indicador = self.ultimo_indicador(regiao)
        cotacao = self.ultima_cotacao_futura()
        cambio = self.ultimo_cambio()

        fisico_cents_libra = arroba_reais_para_cents_libra(
            reais_por_arroba=indicador.reais_por_arroba,
            ptax_venda=cambio.ptax_venda,
        )
        valor = fisico_cents_libra - cotacao.cents_por_libra

        return Basis(
            data=indicador.data,
            regiao=regiao,
            valor_cents_por_libra=valor,
        )
