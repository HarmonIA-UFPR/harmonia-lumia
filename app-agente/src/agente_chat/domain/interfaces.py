# agente_chat/domain/interfaces.py

"""
Interfaces (Ports) do domínio.
Definem os contratos que a infraestrutura deve implementar.
Seguem o padrão Ports & Adapters (Hexagonal Architecture).
"""

from __future__ import annotations

from typing import Any, Protocol

import numpy as np


class IEmbeddingService(Protocol):
    """Serviço de geração de embeddings."""

    def encode(self, textos: list[str]) -> np.ndarray:
        """Gera embeddings normalizados para uma lista de textos."""
        ...


class IRetriever(Protocol):
    """Serviço de busca por similaridade no banco vetorial."""

    def buscar_contexto(
        self,
        query: str,
        perfil: int,
        k: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Retorna até ``k`` contextos relevantes.

        Cada dict contém:
            - tool_description: str
            - tool_name: str
            - tool_uuidv7: str
            - tool_complexity: int
            - score: float
        """
        ...


class ILLMService(Protocol):
    """Serviço de geração de texto via LLM."""

    def gerar_resposta(self, mensagens: list[dict[str, str]]) -> str:
        """Gera uma resposta textual a partir de uma lista de mensagens."""
        ...
