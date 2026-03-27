from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.tool.entity import Tool, ToolComplexity
from app.infrastructure.database.models.tool_model import ToolModel


class ToolRepositoryImpl:
    """
    Implementação concreta do ToolRepository
    usando SQLAlchemy AsyncSession.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_domain(model: ToolModel) -> Tool:
        return Tool(
            tool_uuidv7=model.tool_uuidv7,
            tool_name=model.tool_name,
            tool_description=model.tool_description,
            tool_data_prog=model.tool_data_prog,
            tool_official_link=model.tool_official_link,
            tool_repository_link=model.tool_repository_link,
            tool_documentation_link=model.tool_documentation_link,
            tool_complexity=ToolComplexity(model.tool_complexity),
        )

    @staticmethod
    def _to_model(entity: Tool) -> ToolModel:
        return ToolModel(
            tool_uuidv7=entity.tool_uuidv7,
            tool_name=entity.tool_name,
            tool_description=entity.tool_description,
            tool_data_prog=entity.tool_data_prog,
            tool_official_link=entity.tool_official_link,
            tool_repository_link=entity.tool_repository_link,
            tool_documentation_link=entity.tool_documentation_link,
            tool_complexity=(
                entity.tool_complexity.value
                if isinstance(entity.tool_complexity, ToolComplexity)
                else entity.tool_complexity
            ),
        )

    async def get_by_id(self, tool_id: uuid.UUID) -> Optional[Tool]:
        model = await self._session.scalar(
            select(ToolModel).where(ToolModel.tool_uuidv7 == tool_id)
        )
        if model:
            return self._to_domain(model)
        return None

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[Tool]:
        result = await self._session.scalars(
            select(ToolModel).limit(limit).offset(offset)
        )
        return [self._to_domain(m) for m in result.all()]

    async def exists_by_name(self, name: str) -> bool:
        model = await self._session.scalar(
            select(ToolModel).where(ToolModel.tool_name == name)
        )
        return model is not None

    async def save(self, tool: Tool) -> Tool:
        # Check if exists to update or insert
        model = await self._session.get(ToolModel, tool.tool_uuidv7)
        if model:
            model.tool_name = tool.tool_name
            model.tool_description = tool.tool_description
            model.tool_data_prog = tool.tool_data_prog
            model.tool_official_link = tool.tool_official_link
            model.tool_repository_link = tool.tool_repository_link
            model.tool_documentation_link = tool.tool_documentation_link
            model.tool_complexity = (
                tool.tool_complexity.value
                if isinstance(tool.tool_complexity, ToolComplexity)
                else tool.tool_complexity
            )
        else:
            model = self._to_model(tool)
            self._session.add(model)

        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, tool_id: uuid.UUID) -> None:
        model = await self._session.get(ToolModel, tool_id)
        if model:
            await self._session.delete(model)
            await self._session.commit()
