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


class AnaliseFisico(BaseModel):
    """Saída estruturada do agente analista de mercado físico."""

    model_config = ConfigDict(extra="forbid")

    regiao: Regiao
    tendencia: Tendencia
    basis_cents_lb: float
    comentario: str = Field(min_length=10)
