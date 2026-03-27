"""Domain entity for history_chat_v2 table."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from edwh_uuid7 import uuid7

from .value_objects import ToolRecommendation


@dataclass
class HistoryChat:
    """Aggregate root representing a single chat history entry.

    Maps to: agente.history_chat_v2
    """

    his_session_uuidv7: UUID = field(default_factory=uuid7)
    his_chat_uuidv7: UUID = field(default_factory=uuid7)
    his_user_uuidv7: UUID = field(default_factory=uuid7)
    his_user_profile: int | None = None
    his_user_prompt: str | None = None
    his_tool_recom_jsonb: list[ToolRecommendation] = field(default_factory=list)
    his_tool_recom_composite_type: list[ToolRecommendation] = field(default_factory=list)
    his_llm_response: str | None = None
    his_timestamp: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    # ── helpers ──────────────────────────────────────────────

    def tools_as_jsonb(self) -> list[dict]:
        """Serialize tool recommendations to a JSON-compatible list."""
        if not self.his_tool_recom_jsonb:
            return []
        return [t.to_dict() for t in self.his_tool_recom_jsonb]

    @staticmethod
    def tools_from_jsonb(raw: list[dict] | str | None) -> list[ToolRecommendation]:
        """Deserialize tool recommendations from a list of JSON dicts or JSON string."""
        if not raw:
            return []

        # If raw is a string (PostgreSQL jsonb), parse it
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError:
                return []

        if not isinstance(raw, list):
            return []

        recoms = []
        for r in raw:
            if not isinstance(r, dict):
                continue
            # Handle both "tool_uuid" and "tool_uuidv7" keys
            uuid_val = r.get("tool_uuid") or r.get("tool_uuidv7")
            if uuid_val:
                recoms.append(
                    ToolRecommendation(
                        tool_uuid=UUID(str(uuid_val)),
                        score=Decimal(str(r["score"])),
                    )
                )
        return recoms
