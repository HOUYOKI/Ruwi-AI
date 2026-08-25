"""In-memory visit record for the Ruwi museum experience."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VisitTurn:
    """One visitor interaction within a museum visit."""

    user_message: str
    assistant_message: str
    artifact_id: int | None = None
    language: str = "en"
    sources: list[dict[str, Any]] = field(default_factory=list)


class VisitRecord:
    """Stores the current visit conversation in memory.

    This is intentionally ephemeral:
    - no database
    - no API
    - no credentials
    - no cross-visit persistence
    """

    def __init__(self) -> None:
        self._turns: list[VisitTurn] = []

    def add_turn(
        self,
        user_message: str,
        assistant_message: str,
        *,
        artifact_id: int | None = None,
        language: str = "en",
        sources: list[dict[str, Any]] | None = None,
    ) -> VisitTurn:
        turn = VisitTurn(
            user_message=user_message,
            assistant_message=assistant_message,
            artifact_id=artifact_id,
            language=language,
            sources=list(sources or []),
        )
        self._turns.append(turn)
        return turn

    def get_turns(self) -> list[VisitTurn]:
        """Return a copy so callers cannot mutate the internal record."""
        return list(self._turns)

    def get_recent_turns(self, limit: int = 5) -> list[VisitTurn]:
        """Return the most recent turns, newest last."""
        if limit < 0:
            raise ValueError("limit must be non-negative")
        if limit == 0:
            return []
        return list(self._turns[-limit:])

    def clear(self) -> None:
        """End the current visit and remove its in-memory history."""
        self._turns.clear()

    @property
    def turn_count(self) -> int:
        return len(self._turns)