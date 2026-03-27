from __future__ import annotations

import uuid
from typing import Optional, Protocol, runtime_checkable

from app.domain.tool.entity import Tool


@runtime_checkable
class ToolRepository(Protocol):
    async def get_by_id(self, tool_id: uuid.UUID) -> Optional[Tool]: ...

    async def list_all(
        self, limit: int = 100, offset: int = 0
    ) -> list[Tool]: ...

    async def exists_by_name(self, name: str) -> bool: ...

    async def save(self, tool: Tool) -> Tool: ...

    async def delete(self, tool_id: uuid.UUID) -> None: ...
