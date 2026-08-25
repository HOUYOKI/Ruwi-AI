"""Optional trusted retrieval supporting the Narrator."""

from typing import Protocol

from pydantic import BaseModel, Field

from .tools import is_trusted_url, needs_connector


class EvidenceItem(BaseModel):
    title: str
    publisher: str
    url: str
    supporting_text: str
    source_type: str = "trusted_web"
    relevance_score: float = Field(ge=0, le=1)
    trust_score: float = Field(ge=0, le=1)


class ConnectorResult(BaseModel):
    used: bool = False
    query: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class RetrievalProvider(Protocol):
    def search(self, query: str, artifact: dict) -> list[EvidenceItem]: ...


class ConnectorUnavailableError(RuntimeError):
    pass


class UnavailableRetrievalProvider:
    def search(self, query: str, artifact: dict) -> list[EvidenceItem]:
        raise ConnectorUnavailableError("No external retrieval provider is configured")


class StaticRetrievalProvider:
    """Small injectable provider for tests and curated future adapters."""

    def __init__(self, evidence: list[EvidenceItem]):
        self.evidence = evidence

    def search(self, query: str, artifact: dict) -> list[EvidenceItem]:
        return self.evidence


def _normalize_url(url: str) -> str:
    return url.rstrip("/").lower()


def _rank_evidence(
    evidence: list[EvidenceItem],
    max_items: int = 5,
) -> list[EvidenceItem]:
    """Deduplicate and rank evidence by trust and relevance."""
    unique: dict[str, EvidenceItem] = {}

    for item in evidence:
        key = _normalize_url(item.url)

        existing = unique.get(key)
        if existing is None or (
            item.trust_score,
            item.relevance_score,
        ) > (
            existing.trust_score,
            existing.relevance_score,
        ):
            unique[key] = item

    return sorted(
        unique.values(),
        key=lambda item: (item.trust_score, item.relevance_score),
        reverse=True,
    )[:max_items]


class ConnectorAgent:
    def __init__(self, provider: RetrievalProvider | None = None, trusted_domains: set[str] | None = None):
        self.provider = provider or UnavailableRetrievalProvider()
        self.trusted_domains = trusted_domains or set()

    def retrieve(self, question: str, artifact: dict) -> ConnectorResult:
        if not needs_connector(question, artifact):
            return ConnectorResult(query=question)
        try:
            candidates = self.provider.search(question, artifact) or []
            accepted = [
                item
                for item in candidates
                if is_trusted_url(item.url, self.trusted_domains)
                and item.trust_score >= 0.7
            ]

            accepted = _rank_evidence(accepted)
        except Exception as exc:  # retrieval can never block the Narrator
            return ConnectorResult(query=question, warnings=[f"Connector unavailable: {type(exc).__name__}"])

        warnings = []
        rejected = len(candidates) - len(accepted)
        if rejected:
            warnings.append(f"Rejected {rejected} untrusted or low-trust source(s)")
        return ConnectorResult(used=bool(accepted), query=question, evidence=accepted, warnings=warnings)


def create_connector() -> ConnectorAgent:
    """Default booth-safe Connector. A real provider can be injected later."""
    return ConnectorAgent()
