# tests/test_api.py

"""
Testes do Agente Chat.
- Testes unitários dos schemas e entidades de domínio
- Teste de serialização/deserialização
- Verificação do contrato (sempre 3 tools)
"""

from __future__ import annotations

import pytest
from uuid import UUID

from agente_chat.domain.entities import ChatRequest, ChatResponse, ToolRecommendation
from agente_chat.domain.value_objects import Score, UserProfile
from agente_chat.interface.schemas import (
    ChatRequestSchema,
    ChatResponseSchema,
    ToolRecommendationSchema,
)


# =========================================================
# Testes de Value Objects
# =========================================================


class TestUserProfile:
    """Testes do value object UserProfile."""

    def test_perfil_valido(self) -> None:
        for valor in (1, 2, 3, 4):
            perfil = UserProfile(valor=valor)
            assert perfil.valor == valor

    def test_perfil_invalido_zero(self) -> None:
        with pytest.raises(ValueError, match="entre 1 e 4"):
            UserProfile(valor=0)

    def test_perfil_invalido_cinco(self) -> None:
        with pytest.raises(ValueError, match="entre 1 e 4"):
            UserProfile(valor=5)

    def test_perfil_invalido_negativo(self) -> None:
        with pytest.raises(ValueError, match="entre 1 e 4"):
            UserProfile(valor=-1)


class TestScore:
    """Testes do value object Score."""

    def test_score_valido(self) -> None:
        for valor in (0.0, 0.5, 1.0):
            score = Score(valor=valor)
            assert score.valor == valor

    def test_score_invalido_negativo(self) -> None:
        with pytest.raises(ValueError, match="entre 0.0 e 1.0"):
            Score(valor=-0.1)

    def test_score_invalido_acima(self) -> None:
        with pytest.raises(ValueError, match="entre 0.0 e 1.0"):
            Score(valor=1.1)


# =========================================================
# Testes de Entidades de Domínio
# =========================================================


class TestToolRecommendation:
    """Testes da entidade ToolRecommendation."""

    def test_criacao_padrao(self) -> None:
        tool = ToolRecommendation()
        assert tool.tool_uuid == ""
        assert tool.score == 0.0

    def test_criacao_com_valores(self) -> None:
        tool = ToolRecommendation(tool_uuid="uuid-1", score=0.92)
        assert tool.tool_uuid == "uuid-1"
        assert tool.score == 0.92

    def test_imutabilidade(self) -> None:
        tool = ToolRecommendation(tool_uuid="uuid-1", score=0.92)
        with pytest.raises(AttributeError):
            tool.tool_uuid = "uuid-2"  # type: ignore[misc]


class TestChatRequest:
    """Testes da entidade ChatRequest."""

    def test_criacao(self) -> None:
        req = ChatRequest(
            user_uuid=UUID("019c6dbb-1c92-7d0b-8bf2-f04afc387cb7"),
            user_prompt="Preciso de IA",
            user_profile=2,
        )
        assert req.user_uuid == UUID("019c6dbb-1c92-7d0b-8bf2-f04afc387cb7")
        assert req.user_prompt == "Preciso de IA"
        assert req.user_profile == 2


class TestChatResponse:
    """Testes da entidade ChatResponse."""

    def test_preenche_tools_vazias_automaticamente(self) -> None:
        """Quando há menos de 3 tools, deve preencher com vazias."""
        resp = ChatResponse(
            user_uuid=UUID("019c6dbb-1c92-7d0b-8bf2-f04afc387cb7"),
            user_prompt="teste",
            user_profile=1,
            resposta_llm="Resposta do LLM",
            tools=[ToolRecommendation(tool_uuid="uuid-1", score=0.92)],
        )
        assert len(resp.tools) == 3
        assert resp.tools[0].tool_uuid == "uuid-1"
        assert resp.tools[1].tool_uuid == ""
        assert resp.tools[2].tool_uuid == ""

    def test_sem_tools_preenche_tres_vazias(self) -> None:
        """Quando não há tools, deve preencher 3 vazias."""
        resp = ChatResponse(
            user_uuid="uuid-user",
            user_prompt="teste",
            user_profile=1,
            resposta_llm="Resposta",
        )
        assert len(resp.tools) == 3
        for tool in resp.tools:
            assert tool.tool_uuid == ""
            assert tool.score == 0.0

    def test_tres_tools_mantidas(self) -> None:
        """Quando já há 3 tools, não deve alterar."""
        tools = [
            ToolRecommendation(tool_uuid=f"uuid-{i}", score=0.9 - i * 0.1)
            for i in range(3)
        ]
        resp = ChatResponse(
            user_uuid="uuid-user",
            user_prompt="teste",
            user_profile=2,
            resposta_llm="Resposta",
            tools=tools,
        )
        assert len(resp.tools) == 3
        assert resp.tools[0].tool_uuid == "uuid-0"

    def test_mais_de_tres_tools_trunca(self) -> None:
        """Quando há mais de 3 tools, deve manter as 3 de maior score."""
        tools = [
            ToolRecommendation(tool_uuid=f"uuid-{i}", score=round(0.5 + i * 0.1, 1))
            for i in range(5)
        ]
        resp = ChatResponse(
            user_uuid="uuid-user",
            user_prompt="teste",
            user_profile=3,
            resposta_llm="Resposta",
            tools=tools,
        )
        assert len(resp.tools) == 3
        # As 3 de maior score devem ser mantidas
        scores = [t.score for t in resp.tools]
        assert scores == sorted(scores, reverse=True)


# =========================================================
# Testes de Schemas Pydantic
# =========================================================


class TestChatRequestSchema:
    """Testes do schema de request."""

    def test_validacao_sucesso(self) -> None:
        schema = ChatRequestSchema(
            user_uuid="019c6dbb-1c92-7d0b-8bf2-f04afc387cb7",
            user_prompt="Preciso de uma IA para transcrever áudio",
            user_profile=2,
        )
        assert schema.user_uuid == UUID("019c6dbb-1c92-7d0b-8bf2-f04afc387cb7")
        assert schema.user_profile == 2

    def test_perfil_invalido(self) -> None:
        with pytest.raises(Exception):
            ChatRequestSchema(
                user_uuid="invalid-uuid",
                user_prompt="teste",
                user_profile=5,
            )

    def test_prompt_vazio(self) -> None:
        with pytest.raises(Exception):
            ChatRequestSchema(
                user_uuid="019c6dbb-1c92-7d0b-8bf2-f04afc387cb7",
                user_prompt="",
                user_profile=1,
            )


class TestChatResponseSchema:
    """Testes do schema de response."""

    def test_serializacao_completa(self) -> None:
        schema = ChatResponseSchema(
            user_uuid="019c6dbb-1c92-7d0b-8bf2-f04afc387cb7",
            user_prompt="teste",
            user_profile=2,
            resposta_llm="Resposta do LLM",
            tools=[
                ToolRecommendationSchema(tool_uuid="uuid-1", score=0.92),
                ToolRecommendationSchema(tool_uuid="uuid-2", score=0.87),
                ToolRecommendationSchema(tool_uuid="", score=0.0),
            ],
        )
        data = schema.model_dump()
        assert str(data["user_uuid"]) == "019c6dbb-1c92-7d0b-8bf2-f04afc387cb7"
        assert len(data["tools"]) == 3
        assert data["tools"][2]["tool_uuid"] == ""
        assert data["tools"][2]["score"] == 0.0

    def test_json_roundtrip(self) -> None:
        """Verifica serialização e deserialização JSON."""
        original = ChatResponseSchema(
            user_uuid="019c6dbb-1c92-7d0b-8bf2-f04afc387cb7",
            user_prompt="teste",
            user_profile=1,
            resposta_llm="Resposta",
            tools=[
                ToolRecommendationSchema(tool_uuid="a", score=0.9),
                ToolRecommendationSchema(tool_uuid="b", score=0.8),
                ToolRecommendationSchema(tool_uuid="", score=0.0),
            ],
        )
        json_str = original.model_dump_json()
        restaurado = ChatResponseSchema.model_validate_json(json_str)
        assert restaurado == original
