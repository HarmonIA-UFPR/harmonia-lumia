# app/application/tool/dto.py
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.tool.entity import ToolComplexity

# ─── Base compartilhada ──────────────────────────────────────────────────────


class ToolBase(BaseModel):
    """Campos comuns a múltiplos DTOs."""

    tool_name: str
    tool_description: str
    tool_data_prog: bool
    tool_official_link: Optional[str] = None
    tool_repository_link: Optional[str] = None
    tool_documentation_link: Optional[str] = None
    tool_complexity: ToolComplexity = ToolComplexity.INICIANTE

    model_config = ConfigDict(
        use_enum_values=True,  # serializa como int no JSON
    )


# ─── Entrada (request) ───────────────────────────────────────────────────────


class ToolCreateDTO(ToolBase):
    """POST /tools — criação de nova tool."""

    pass


class ToolUpdateDTO(BaseModel):
    """PATCH /tools/{id} — atualização parcial (todos opcionais)."""

    tool_name: Optional[str] = None
    tool_description: Optional[str] = None
    tool_data_prog: Optional[bool] = None
    tool_official_link: Optional[str] = None
    tool_repository_link: Optional[str] = None
    tool_documentation_link: Optional[str] = None
    tool_complexity: Optional[ToolComplexity] = None

    model_config = ConfigDict(use_enum_values=True)


# ─── Saída (response) ────────────────────────────────────────────────────────


class ToolPublicDTO(ToolBase):
    """Resposta pública da ferramenta."""

    tool_uuidv7: UUID

    model_config = ConfigDict(
        from_attributes=True,  # permite model_validate(orm_object)
        use_enum_values=True,
    )


class ToolListDTO(BaseModel):
    """Resposta para listagem de ferramentas."""

    tools: list[ToolPublicDTO]
    total: int = Field(default=0, description='Total de registros')
