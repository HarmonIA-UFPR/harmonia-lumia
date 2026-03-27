# app/application/tool/service.py
from __future__ import annotations

import uuid

from app.application.tool.dto import (
    ToolCreateDTO,
    ToolPublicDTO,
    ToolUpdateDTO,
)
from app.domain.tool.entity import Tool
from app.domain.tool.exceptions import (
    ToolAlreadyExistsException,
    ToolNotFoundException,
)
from app.domain.tool.repository import ToolRepository


class ToolService:
    """Orquestra os casos de uso do domínio Tool."""

    def __init__(self, repository: ToolRepository) -> None:
        self._repo = repository

    async def create_tool(self, dto: ToolCreateDTO) -> ToolPublicDTO:
        if await self._repo.exists_by_name(dto.tool_name):
            raise ToolAlreadyExistsException()
        tool = Tool(
            tool_name=dto.tool_name,
            tool_description=dto.tool_description,
            tool_data_prog=dto.tool_data_prog,
            tool_official_link=dto.tool_official_link,
            tool_repository_link=dto.tool_repository_link,
            tool_documentation_link=dto.tool_documentation_link,
            tool_complexity=dto.tool_complexity,
        )
        saved = await self._repo.save(tool)
        return ToolPublicDTO.model_validate(saved)

    async def get_tool(self, tool_id: uuid.UUID) -> ToolPublicDTO:
        tool = await self._repo.get_by_id(tool_id)
        if not tool:
            raise ToolNotFoundException()
        return ToolPublicDTO.model_validate(tool)

    async def list_tools(self, limit: int = 100, offset: int = 0) -> dict:
        tools = await self._repo.list_all(limit=limit, offset=offset)
        return {
            'tools': [ToolPublicDTO.model_validate(t) for t in tools],
            'total': len(tools),
        }

    async def update_tool(
        self, tool_id: uuid.UUID, dto: ToolUpdateDTO
    ) -> ToolPublicDTO:
        tool = await self._repo.get_by_id(tool_id)
        if not tool:
            raise ToolNotFoundException()

        # Update fields dynamically
        for field, value in dto.model_dump(exclude_unset=True).items():
            setattr(tool, field, value)

        updated = await self._repo.save(tool)
        return ToolPublicDTO.model_validate(updated)

    async def delete_tool(self, tool_id: uuid.UUID) -> ToolPublicDTO:
        tool = await self._repo.get_by_id(tool_id)
        if not tool:
            raise ToolNotFoundException()
        snapshot = ToolPublicDTO.model_validate(tool)
        await self._repo.delete(tool_id)
        return snapshot
