from __future__ import annotations

import uuid
from typing import Optional, Protocol, runtime_checkable

from app.domain.user.entity import User, UserProfile


@runtime_checkable
class UserRepository(Protocol):
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]: ...

    async def get_by_email(self, email: str) -> Optional[User]: ...

    async def get_by_profile(self, profile: UserProfile) -> list[User]: ...

    async def list_all(
        self, limit: int = 100, offset: int = 0
    ) -> list[User]: ...

    async def save(self, user: User) -> User: ...

    async def delete(self, user_id: uuid.UUID) -> None: ...

    async def exists_by_email(self, email: str) -> bool: ...
