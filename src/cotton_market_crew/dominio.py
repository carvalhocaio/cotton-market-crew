"""Modelos de domínio da mesa de comercialização de algodão.

Value objects imutáveis (frozen dataclasses) que representam os fatos de
mercado usados no boletim semanal. Validação acontece na fronteira de
construção do objeto: se o dataclass foi criado, ele é válido.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


class MercadoAlgodaoError(Exception):
    """Erro base do domínio de mercado de algodão."""


class IndicadorInvalidoError(MercadoAlgodaoError):
    """Levantado quando um indicador físico não passa na validação."""


class CotacaoInvalidaError(MercadoAlgodaoError):
    """Levantado quando uma cotação futura ou câmbio é inválido."""


class BasisInvalidoError(MercadoAlgodaoError):
    """Levantado quando um basis não passa na validação."""


REGIOES_VALIDAS = frozenset({"MT", "BA", "GO"})


def _validar_regiao(regiao: str, excecao: type[MercadoAlgodaoError]) -> None:
    if regiao not in REGIOES_VALIDAS:
        regioes = ", ".join(sorted(REGIOES_VALIDAS))
        raise excecao(f"Região '{regiao}' inválida. Use uma de: {regioes}.")


def _validar_positivo(
    valor: Decimal, nome_campo: str, excecao: type[MercadoAlgodaoError]
) -> None:
    if valor <= 0:
        raise excecao(f"'{nome_campo}' deve ser positivo, recebido: {valor}.")


@dataclass(frozen=True, slots=True)
class IndicadorFisico:
    """Indicador de preço físico do algodão (estilo CEPEA/ESALQ)."""

    data: date
    regiao: str
    reais_por_arroba: Decimal
    fonte: str = "CEPEA/ESALQ"

    def __post_init__(self) -> None:
        _validar_regiao(self.regiao, IndicadorInvalidoError)
        _validar_positivo(
            self.reais_por_arroba, "reais_por_arroba", IndicadorInvalidoError
        )


@dataclass(frozen=True, slots=True)
class CotacaoFutura:
    """Cotação do contrato futuro de algodão (ICE Futures US n.º 2)."""

    data: date
    contrato: str
    cents_por_libra: Decimal
    fonte: str = "ICE Futures US #2"

    def __post_init__(self) -> None:
        _validar_positivo(self.cents_por_libra, "cents_por_libra", CotacaoInvalidaError)


@dataclass(frozen=True, slots=True)
class Cambio:
    """Taxa de câmbio PTAX de venda (R$/US$) do dia."""

    data: date
    ptax_venda: Decimal

    def __post_init__(self) -> None:
        _validar_positivo(self.ptax_venda, "ptax_venda", CotacaoInvalidaError)


@dataclass(frozen=True, slots=True)
class Basis:
    """Basis regional: físico convertido menos o futuro, em cents/lb.

    Valor negativo é comum e esperado (físico brasileiro tipicamente
    desconta contra o contrato futuro).
    """

    data: date
    regiao: str
    valor_cents_por_libra: Decimal

    def __post_init__(self) -> None:
        _validar_regiao(self.regiao, BasisInvalidoError)
