"""PostgreSQL repository implementation for HistoryChat."""

from __future__ import annotations

import json
import uuid

import asyncpg

from agente_chat.config.settings import settings
from agente_chat.domain.history_chat.entity import HistoryChat
from agente_chat.domain.history_chat.repositories import IHistoryChatRepository
from agente_chat.domain.history_chat.value_objects import ToolRecommendation


class PostgresHistoryChatRepository(IHistoryChatRepository):
    """PostgreSQL adapter for HistoryChat persistence."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool
        self._schema = settings.AGENTE_SCHEMA
        self._table = f'{self._schema}.history_chat_v2'

    @classmethod
    async def create_pool(cls) -> asyncpg.Pool:
        """Create a new connection pool."""
        return await asyncpg.create_pool(
            host=settings.AGENTE_HOST,
            port=settings.AGENTE_PORT,
            database=settings.AGENTE_DB,
            user=settings.AGENTE_USER,
            password=settings.AGENTE_PASSWORD,
            min_size=1,
            max_size=10,
        )

    async def save(self, entity: HistoryChat) -> HistoryChat:
        """Persist a new chat entry."""
        tools_json = json.dumps(entity.tools_as_jsonb()) if entity.his_tool_recom_jsonb else None
        
        tools_composite = None
        if entity.his_tool_recom_composite_type:
            tools_composite = [
                (str(t.tool_uuid), float(t.score))
                for t in entity.his_tool_recom_composite_type
            ]

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                f"""
                INSERT INTO {self._table} (
                    his_session_uuidv7, his_chat_uuidv7, his_user_uuidv7,
                    his_user_profile, his_user_prompt, his_tool_recom_jsonb,
                    his_tool_recom_composite_type, his_llm_response, his_timestamp
                ) VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7::agente.tool_recommendation[], $8, $9)
                RETURNING *
                """,
                entity.his_session_uuidv7,
                entity.his_chat_uuidv7,
                entity.his_user_uuidv7,
                entity.his_user_profile,
                entity.his_user_prompt,
                tools_json,
                tools_composite,
                entity.his_llm_response,
                entity.his_timestamp,
            )

        return self._row_to_entity(row)

    async def find_by_session(self, session_uuid: uuid.UUID) -> list[HistoryChat]:
        """Retrieve all chat entries for a given session."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT * FROM {self._table}
                WHERE his_session_uuidv7 = $1
                ORDER BY his_timestamp ASC
                """,
                session_uuid,
            )
        return [self._row_to_entity(row) for row in rows]

    async def find_by_user(self, user_uuid: uuid.UUID) -> list[HistoryChat]:
        """Retrieve all chat entries for a given user."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT * FROM {self._table}
                WHERE his_user_uuidv7 = $1
                ORDER BY his_timestamp DESC
                """,
                user_uuid,
            )
        return [self._row_to_entity(row) for row in rows]

    async def find_sessions_by_user(self, user_uuid: uuid.UUID) -> list[uuid.UUID]:
        """Retrieve all unique sessions for a user."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT DISTINCT his_session_uuidv7 FROM {self._table}
                WHERE his_user_uuidv7 = $1
                ORDER BY his_session_uuidv7
                """,
                user_uuid,
            )
        return [row["his_session_uuidv7"] for row in rows]

    async def find_by_id(self, chat_uuid: uuid.UUID) -> HistoryChat | None:
        """Retrieve a chat entry by its UUID."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                f"""
                SELECT * FROM {self._table}
                WHERE his_chat_uuidv7 = $1
                """,
                chat_uuid,
            )
        if row is None:
            return None
        return self._row_to_entity(row)

    async def update(self, entity: HistoryChat) -> HistoryChat:
        """Update an existing chat entry."""
        tools_json = json.dumps(entity.tools_as_jsonb()) if entity.his_tool_recom_jsonb else None
        
        tools_composite = None
        if entity.his_tool_recom_composite_type:
            tools_composite = [
                (str(t.tool_uuid), float(t.score))
                for t in entity.his_tool_recom_composite_type
            ]

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                f"""
                UPDATE {self._table}
                SET his_session_uuidv7 = $1,
                    his_user_uuidv7 = $2,
                    his_user_profile = $3,
                    his_user_prompt = $4,
                    his_tool_recom_jsonb = $5::jsonb,
                    his_tool_recom_composite_type = $6::agente.tool_recommendation[],
                    his_llm_response = $7,
                    his_timestamp = $8
                WHERE his_chat_uuidv7 = $9
                RETURNING *
                """,
                entity.his_session_uuidv7,
                entity.his_user_uuidv7,
                entity.his_user_profile,
                entity.his_user_prompt,
                tools_json,
                tools_composite,
                entity.his_llm_response,
                entity.his_timestamp,
                entity.his_chat_uuidv7,
            )

        if row is None:
            raise ValueError(f"Chat with UUID {entity.his_chat_uuidv7} not found")

        return self._row_to_entity(row)

    async def delete(self, chat_uuid: uuid.UUID) -> bool:
        """Delete a chat entry by its UUID."""
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                f"""
                DELETE FROM {self._table}
                WHERE his_chat_uuidv7 = $1
                """,
                chat_uuid,
            )
        # asyncpg returns 'DELETE <count>'
        return result != "DELETE 0"

    async def list_all(
        self, limit: int = 100, offset: int = 0
    ) -> tuple[list[HistoryChat], int]:
        """List all chat entries with pagination. Returns (items, total_count)."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT * FROM {self._table}
                ORDER BY his_timestamp DESC
                LIMIT $1 OFFSET $2
                """,
                limit,
                offset,
            )
            count_row = await conn.fetchrow(
                f"SELECT COUNT(*) as total FROM {self._table}"
            )

        total = count_row["total"] if count_row else 0
        return [self._row_to_entity(row) for row in rows], total

    def _row_to_entity(self, row: asyncpg.Record) -> HistoryChat:
        """Convert a database row to a HistoryChat entity."""
        tools: list[ToolRecommendation] = []
        if row["his_tool_recom_jsonb"]:
            tools = HistoryChat.tools_from_jsonb(row["his_tool_recom_jsonb"])

        return HistoryChat(
            his_session_uuidv7=row["his_session_uuidv7"],
            his_chat_uuidv7=row["his_chat_uuidv7"],
            his_user_uuidv7=row["his_user_uuidv7"],
            his_user_profile=row["his_user_profile"],
            his_user_prompt=row["his_user_prompt"],
            his_tool_recom_jsonb=tools,
            his_tool_recom_composite_type=[],  # Simplified - not using composite type
            his_llm_response=row["his_llm_response"],
            his_timestamp=row["his_timestamp"],
        )
