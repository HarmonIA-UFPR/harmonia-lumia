import enum
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from edwh_uuid7 import uuid7


class ToolComplexity(enum.IntEnum):
    INICIANTE = 1
    INTERMEDIARIO = 2
    AVANCADO = 3
    EXPERT = 4


@dataclass
class Tool:
    tool_name: str
    tool_description: str
    tool_data_prog: bool
    tool_official_link: Optional[str] = None
    tool_repository_link: Optional[str] = None
    tool_documentation_link: Optional[str] = None
    tool_complexity: ToolComplexity = ToolComplexity.INICIANTE
    tool_uuidv7: UUID = field(default_factory=uuid7)
