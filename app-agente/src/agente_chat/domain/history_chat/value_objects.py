"""Domain value objects for the chat bounded context."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ToolRecommendation:
    """Immutable value object representing a single tool recommendation."""

    tool_uuid: uuid.UUID
    score: Decimal

    def to_dict(self) -> dict:
        return {
            "tool_uuid": str(self.tool_uuid),
            "score": float(self.score),
        }
