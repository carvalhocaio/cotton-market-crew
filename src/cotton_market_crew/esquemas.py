"""Esquemas Pydantic da fronteira LLM -> domínio.

Diferente dos value objects em `dominio.py` (fatos de mercado, imutáveis
e construídos pelo `MercadoStore`), os esquemas aqui representam
*interpretação* produzida por um agente CrewAI via `Task(output_pydantic=...)`.
A validação aqui restringe o formato da resposta; validar se os números
batem com o que o `MercadoStore` calculou de fato é responsabilidade do
guardrail, não deste módulo.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Regiao = Literal["MT", "BA", "GO"]
Tendencia = Literal["alta", "queda", "estavel"]
PressaoCambial = Literal["favoravel", "desfavoravel", "neutra"]


class AnaliseFisico(BaseModel):
    """Saída estruturada do agente analista de mercado físico."""

    model_config = ConfigDict(extra="forbid")

    regiao: Regiao
    tendencia: Tendencia
    basis_cents_lb: float
    comentario: str = Field(min_length=10)


class AnaliseConsolidada(BaseModel):
    """Saída estruturada do agente estrategista, consolidando os analistas."""

    model_config = ConfigDict(extra="forbid")

    tendencia_geral: Tendencia
    regiao_destaque: Regiao
    basis_medio_cents_lb: float
    comentario_estrategico: str = Field(min_length=30)


class AnaliseMercadoExterno(BaseModel):
    """Saída estruturada do agente analista de mercado externo."""

    model_config = ConfigDict(extra="forbid")

    tendencia_futuro: Tendencia
    pressao_cambial: PressaoCambial
    comentario: str = Field(min_length=10)
