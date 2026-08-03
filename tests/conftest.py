"""Fixtures compartilhadas entre módulos de teste."""

import pytest
from crewai.llm import BaseLLM


class LLMFalso(BaseLLM):
    """Duplo de teste: satisfaz o contrato de BaseLLM sem chamar API real."""

    def __init__(self) -> None:
        super().__init__(model="falso/modelo-de-teste")

    def call(self, *args, **kwargs):
        return "resposta falsa"


@pytest.fixture
def llm_falso() -> LLMFalso:
    return LLMFalso()
