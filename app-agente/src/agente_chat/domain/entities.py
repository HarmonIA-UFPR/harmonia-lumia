# agente_chat/domain/entities.py

"""
Entidades de domínio do Agente Chat.
Representam os objetos centrais do negócio — sem dependências externas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ToolRecommendation:
    """Uma recomendação de ferramenta com seu score de similaridade."""

    tool_uuid: UUID | str = ""
    score: float = 0.0


@dataclass(frozen=True, slots=True)
class ChatRequest:
    """Requisição de chat recebida pelo agente."""

    user_uuid: UUID
    user_prompt: str
    user_profile: int


@dataclass(slots=True)
class ChatResponse:
    """Resposta completa do agente — sempre com exatamente 3 tools."""

    user_uuid: UUID
    user_prompt: str
    user_profile: int
    resposta_llm: str
    tools: list[ToolRecommendation] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Garante que a lista de tools sempre tenha exatamente 3 elementos."""
        self._normalizar_tools()

    def _normalizar_tools(self) -> None:
        """Preenche posições faltantes com ToolRecommendation vazia e limita a 3 ferramentas."""
        while len(self.tools) < 3:
            self.tools.append(ToolRecommendation())
        if len(self.tools) > 3:
            self.tools = sorted(self.tools, key=lambda t: t.score, reverse=True)[:3]
