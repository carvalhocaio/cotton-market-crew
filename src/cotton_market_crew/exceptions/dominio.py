"""Exceções do domínio de mercado de algodão."""


class MercadoAlgodaoError(Exception):
    """Erro base do domínio de mercado de algodão."""


class IndicadorInvalidoError(MercadoAlgodaoError):
    """Levantado quando um indicador físico não passa na validação."""


class CotacaoInvalidaError(MercadoAlgodaoError):
    """Levantado quando uma cotação futura ou câmbio é inválido."""


class BasisInvalidoError(MercadoAlgodaoError):
    """Levantado quando um basis não passa na validação."""
