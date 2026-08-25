"""In-memory store for isolated Ruwi visitor sessions."""

from .record import VisitRecord



class VisitStore:
    """Keeps independent VisitRecord instances keyed by visit ID."""

    def __init__(self) -> None:
        self._visits: dict[str, VisitRecord] = {}

    def get_or_create(self, visit_id: str) -> VisitRecord:
        """Return the visit for an ID, creating it when needed."""
        if not visit_id:
            raise ValueError("visit_id must not be empty")

        if visit_id not in self._visits:
            self._visits[visit_id] = VisitRecord()

        return self._visits[visit_id]

    def get(self, visit_id: str) -> VisitRecord | None:
        """Return an existing visit without creating a new one."""
        return self._visits.get(visit_id)

    def delete(self, visit_id: str) -> bool:
        """Delete a visit and return whether it existed."""
        return self._visits.pop(visit_id, None) is not None

    def clear(self) -> None:
        """End all active in-memory visits."""
        self._visits.clear()

    @property
    def visit_count(self) -> int:
        return len(self._visits)