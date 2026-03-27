# agente_chat/interface/schemas.py

"""
Schemas Pydantic para a API do Agente Chat.
Inclui schemas para Chat e HistoryChat.
"""

from __future__ import annotations

from uuid import UUID

from edwh_uuid7 import uuid7
from pydantic import BaseModel, Field

# ============================================================================
# Chat Schemas (existentes)
# ============================================================================

class ToolRecommendationSchema(BaseModel):
    """Schema de uma recomendação de ferramenta."""

    tool_uuid: UUID | str = Field(default="", description="UUID da ferramenta recomendada")
    score: float = Field(default=0.0, ge=0.0, le=1.0, description="Score de similaridade (0.0 a 1.0)")


class ChatRequestSchema(BaseModel):
    """Schema de entrada — requisição de chat."""

    user_uuid: UUID = Field(default_factory=uuid7, description="UUID do usuário")
    user_prompt: str = Field(..., min_length=1, description="Texto da dúvida do usuário")
    user_profile: int = Field(..., ge=1, le=4, description="Perfil técnico (1=iniciante, 4=expert)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_uuid": "019c6dbb-1c92-7d0b-8bf2-f04afc387cb7",
                    "user_prompt": "Preciso de uma IA para transcrever áudio",
                    "user_profile": 2,
                }
            ]
        }
    }


class HistoryChatRequestSchema(ChatRequestSchema):
    """Schema de entrada — requisição de history-chat.
    Suporta omitir ou enviar uma sessão existente."""

    his_session_uuidv7: UUID | None = Field(
        default=None, 
        description="UUID da sessão (se não fornecido, será gerado um novo no backend)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "his_session_uuidv7": "019c6dbb-1c92-7d0b-8bf2-f04afc387cb7",
                    "user_uuid": "019c6dbb-1c92-7d0b-8bf2-f04afc387cb7",
                    "user_prompt": "Preciso de uma IA para transcrever áudio",
                    "user_profile": 2,
                }
            ]
        }
    }


class ChatResponseSchema(BaseModel):
    """Schema de saída — resposta do agente."""

    user_uuid: UUID = Field(..., description="UUID do usuário (eco)")
    user_prompt: str = Field(..., description="Prompt original (eco)")
    user_profile: int = Field(..., description="Perfil técnico (eco)")
    resposta_llm: str = Field(..., description="Texto descritivo gerado pelo LLM")
    tools: list[ToolRecommendationSchema] = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Exatamente 3 ferramentas recomendadas",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_uuid": "019c6dbb-1c92-7d0b-8bf2-f04afc387cb7",
                    "user_prompt": "Preciso de uma IA para transcrever áudio",
                    "user_profile": 2,
                    "resposta_llm": "Baseado no seu perfil intermediário, recomendo...",
                    "tools": [
                        {"tool_uuid": "uuid-1", "score": 0.92},
                        {"tool_uuid": "uuid-2", "score": 0.87},
                        {"tool_uuid": "", "score": 0.0},
                    ],
                }
            ]
        }
    }


# ============================================================================
# HistoryChat Schemas (novos)
# ============================================================================

class HistoryChatBaseSchema(BaseModel):
    """Base schema for HistoryChat - campos comuns."""

    his_session_uuidv7: UUID = Field(default_factory=uuid7, description="UUID da sessão")
    his_user_uuidv7: UUID = Field(default_factory=uuid7, description="UUID do usuário")
    his_user_profile: int | None = Field(None, description="Perfil do usuário")
    his_user_prompt: str | None = Field(None, description="Prompt do usuário")
    his_tool_recom_jsonb: list[ToolRecommendationSchema] = Field(
        default_factory=list, description="Recomendações de ferramentas (JSONB)"
    )
    his_llm_response: str | None = Field(None, description="Resposta do LLM")


class HistoryChatCreateSchema(HistoryChatBaseSchema):
    """Schema para criação de um HistoryChat."""

    pass


class HistoryChatUpdateSchema(BaseModel):
    """Schema para atualização parcial de um HistoryChat."""

    his_session_uuidv7: UUID | None = Field(None, description="UUID da sessão")
    his_user_uuidv7: UUID | None = Field(None, description="UUID do usuário")
    his_user_profile: int | None = Field(None, description="Perfil do usuário")
    his_user_prompt: str | None = Field(None, description="Prompt do usuário")
    his_tool_recom_jsonb: list[ToolRecommendationSchema] | None = Field(
        None, description="Recomendações de ferramentas (JSONB)"
    )
    his_llm_response: str | None = Field(None, description="Resposta do LLM")


class HistoryChatResponseSchema(BaseModel):
    """Schema de resposta completo de um HistoryChat."""

    his_session_uuidv7: UUID = Field(..., description="UUID da sessão")
    his_chat_uuidv7: UUID = Field(..., description="UUID do chat (PK)")
    his_user_uuidv7: UUID = Field(..., description="UUID do usuário")
    his_user_profile: int | None = Field(None, description="Perfil do usuário")
    his_user_prompt: str | None = Field(None, description="Prompt do usuário")
    his_tool_recom_jsonb: list[ToolRecommendationSchema] = Field(
        default_factory=list, description="Recomendações de ferramentas (JSONB)"
    )
    his_llm_response: str | None = Field(None, description="Resposta do LLM")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "his_session_uuidv7": "019c6dbb-1c92-7d0b-8bf2-f04afc387cb7",
                    "his_chat_uuidv7": "019c6dbb-1c92-7d0b-8bf2-f04afc387cb8",
                    "his_user_uuidv7": "019c6dbb-1c92-7d0b-8bf2-f04afc387cb9",
                    "his_user_profile": 2,
                    "his_user_prompt": "Preciso de uma IA para transcrever áudio",
                    "his_tool_recom_jsonb": [
                        {"tool_uuid": "uuid-1", "score": 0.92},
                        {"tool_uuid": "uuid-2", "score": 0.87},
  {"tool_uuid": "uuid-3", "score": 0.87},
                    ],
                    "his_llm_response": "Baseado no seu perfil...",
                }
            ]
        }
    }


class HistoryChatListResponseSchema(BaseModel):
    """Schema para listagem paginada de HistoryChat."""

    history_chats: list[HistoryChatResponseSchema]
    total: int
    limit: int
    offset: int
