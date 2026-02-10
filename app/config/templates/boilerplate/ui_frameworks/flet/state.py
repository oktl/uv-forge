"""Application state for {{project_name}}."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AppState:
    """Single source of truth for mutable application state."""

    title: str = "{{project_name}}"
    settings: dict[str, Any] = field(default_factory=dict)
