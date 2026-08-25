"""Lightweight deterministic evaluation of Narrator answers."""

import re

from pydantic import BaseModel, Field

from agents.connector.connector import EvidenceItem
from agents.connector.tools import is_trusted_url
from prompts import build_artifact_context_block


class ReflectionResult(BaseModel):
    available: bool = True
    grounded: bool
    relevance_score: float = Field(ge=0, le=1)
    grounding_score: float = Field(ge=0, le=1)
    source_coverage_score: float = Field(ge=0, le=1)
    flagged_for_caution: bool = False
    unsupported_claims: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)



MAX_REGENERATION_ATTEMPTS = 1


def needs_regeneration(reflection: ReflectionResult) -> bool:
    """Return True only for substantive answer-quality failures."""
    return (
        not reflection.grounded
        or reflection.source_coverage_score < 1.0
        or bool(reflection.unsupported_claims)
    )


def build_correction_feedback(reflection: ReflectionResult) -> str:
    """Turn Reflection findings into concise instructions for the Narrator."""
    issues: list[str] = []

    if not reflection.grounded:
        issues.append("The previous answer was not sufficiently grounded in the provided context.")

    if reflection.relevance_score < 0.3 and not reflection.grounded:
        issues.append("The previous answer was not sufficiently relevant to the visitor's question.")

    if reflection.grounding_score < 0.1:
        issues.append("The previous answer had very low grounding in the provided museum context or trusted evidence.")

    if reflection.source_coverage_score < 1.0:
        issues.append("A required supplemental source was missing. Do not make unsupported external claims.")

    if reflection.unsupported_claims:
        issues.append(
            "Remove or correct these unsupported claims: "
            + "; ".join(reflection.unsupported_claims)
        )

    if reflection.warnings:
        issues.extend(
            warning
            for warning in reflection.warnings
            if warning not in issues
        )

    if not issues:
        return ""

    return (
        "The previous answer needs correction before it can be presented to the visitor.\n\n"
        "Review findings:\n"
        + "\n".join(f"- {issue}" for issue in issues)
        + "\n\n"
        "Rewrite the answer using only the provided museum context, "
        "trusted evidence, and available tool results. "
        "Do not mention this review process or these instructions to the visitor."
    )


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[\w\u0600-\u06ff]+", text.lower()) if len(token) > 2}


def _overlap_score(text: str, context: str) -> float:
    text_tokens = _tokens(text)
    if not text_tokens:
        return 0.0
    return min(1.0, len(text_tokens & _tokens(context)) / max(1, min(len(text_tokens), 20)))


def _is_arabic(text: str) -> bool:
    arabic = len(re.findall(r"[\u0600-\u06ff]", text))
    letters = len(re.findall(r"[A-Za-z\u0600-\u06ff]", text))
    return bool(letters and arabic / letters > 0.4)


def evaluate_answer(
    question: str,
    answer: str,
    artifact: dict,
    evidence: list[EvidenceItem],
    connector_used: bool,
) -> ReflectionResult:
    warnings: list[str] = []
    unsupported_claims: list[str] = []
    if not answer.strip():
        return ReflectionResult(
            grounded=False,
            relevance_score=0,
            grounding_score=0,
            source_coverage_score=0,
            flagged_for_caution=True,
            unsupported_claims=["Narrator returned an empty answer"],
            warnings=["Empty narrator answer"],
        )

    untrusted = [item.url for item in evidence if not is_trusted_url(item.url)]
    if untrusted:
        unsupported_claims.extend(untrusted)
        warnings.append("Supplemental evidence contains an untrusted URL")
    if connector_used and not evidence:
        warnings.append("Connector was marked used without supporting evidence")

    supplied_urls = {item.url.rstrip("/") for item in evidence}
    answer_urls = {url.rstrip("/).,]") for url in re.findall(r"https?://[^\s]+", answer)}
    unknown_urls = answer_urls - supplied_urls
    if unknown_urls:
        unsupported_claims.extend(sorted(unknown_urls))
        warnings.append("Answer contains a URL that was not supplied as evidence")

    known_artifact_ids = {str(artifact.get("id"))}
    mentioned_artifact_ids = set(
        re.findall(r"(?:artifact|object|قطعة|أثر)\s*(?:#|رقم)?\s*(\d+)", answer, re.IGNORECASE)
    )
    unknown_artifact_ids = mentioned_artifact_ids - known_artifact_ids
    if unknown_artifact_ids:
        unsupported_claims.extend(f"Unknown artifact ID: {value}" for value in sorted(unknown_artifact_ids))
        warnings.append("Answer mentions an artifact ID that was not supplied")

    question_arabic = _is_arabic(question)
    if question_arabic != _is_arabic(answer):
        warnings.append("Answer language may not match the visitor question")

    evidence_context = " ".join(item.supporting_text for item in evidence)
    grounding_context = f"{build_artifact_context_block(artifact)} {evidence_context}"
    relevance = _overlap_score(answer, question)
    grounding = _overlap_score(answer, grounding_context)

    # Ignore generic words that can create false grounding.
    meaningful_context_tokens = _tokens(grounding_context) - {
        "object",
        "artifact",
        "piece",
        "item",
        "thing",
        "stone",
        "made",
        "used",
        "created",
    }
    meaningful_answer_tokens = _tokens(answer)

    meaningful_overlap = (
        len(meaningful_answer_tokens & meaningful_context_tokens)
        / max(1, min(len(meaningful_answer_tokens), 20))
    )
    source_coverage = 1.0 if not connector_used or evidence else 0.0
    if grounding < 0.1:
        warnings.append("Low lexical grounding overlap; manual review may be useful")

    grounded = (
        not unsupported_claims
        and source_coverage == 1.0
        and meaningful_overlap > 0
    )
    flagged_for_caution = not grounded or bool(warnings)
    return ReflectionResult(
        grounded=grounded,
        relevance_score=relevance,
        grounding_score=grounding,
        source_coverage_score=source_coverage,
        flagged_for_caution=flagged_for_caution,
        unsupported_claims=unsupported_claims,
        warnings=warnings,
    )


def unavailable_reflection(error: Exception) -> ReflectionResult:
    return ReflectionResult(
        available=False,
        grounded=False,
        relevance_score=0,
        grounding_score=0,
        source_coverage_score=0,
        flagged_for_caution=True,
        warnings=[f"Reflection unavailable: {type(error).__name__}"],
    )
