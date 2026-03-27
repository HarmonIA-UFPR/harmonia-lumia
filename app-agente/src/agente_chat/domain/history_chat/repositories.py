"""Abstract repository interface (port) for HistoryChat persistence."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from agente_chat.domain.history_chat.entity import HistoryChat


class IHistoryChatRepository(ABC):
    """Port — defines the contract for chat history persistence."""

    @abstractmethod
    async def save(self, entity: HistoryChat) -> HistoryChat:
        """Persist a new chat entry and return it with DB-generated fields."""
        ...

    @abstractmethod
    async def find_by_session(self, session_uuid: uuid.UUID) -> list[HistoryChat]:
        """Retrieve all chat entries for a given session."""
        ...

    @abstractmethod
    async def find_by_user(self, user_uuid: uuid.UUID) -> list[HistoryChat]:
        """Retrieve all chat entries for a given user."""
        ...

    @abstractmethod
    async def find_sessions_by_user(
        self, user_uuid: uuid.UUID
    ) -> list[uuid.UUID]:
        """Retrieve all unique sessions for a user."""
        ...
