"""Deterministic Connector intent and trusted-source policy."""

from urllib.parse import urlparse


CONNECTOR_INTENT_TERMS = (
    # English
    "another civilization",
    "other civilization",
    "other culture",
    "elsewhere",
    "similar object",
    "similar objects",
    "influence",
    "influenced",
    "historical event",
    "compare",
    "comparison",
    "connected to",
    "relationship to",
    "broader significance",

    # Arabic
    "حضارة أخرى",
    "حضارات أخرى",
    "ثقافة أخرى",
    "ثقافات أخرى",
    "أماكن أخرى",
    "قطع مشابهة",
    "أشياء مشابهة",
    "تأثير",
    "تأثر",
    "حدث تاريخي",
    "قارن",
    "مقارنة",
    "ارتباط بـ",
    "ارتباط ب",
    "مرتبط بـ",
    "مرتبط ب",
    "علاقة بـ",
    "علاقة ب",
    "ما علاقته",
    "هل تأثر",
    "هل تأثر بـ",
)


DEFAULT_TRUSTED_DOMAINS = {
    "nationalmuseum.moc.gov.sa",
    "moc.gov.sa",
    "heritage.moc.gov.sa",
    "saudipedia.com",
    "unesco.org",
    "metmuseum.org",
    "britishmuseum.org",
    "si.edu",
}


def needs_connector(question: str, artifact_context: dict | None = None) -> bool:
    """Return whether the question asks beyond the local museum record.

    ``artifact_context`` is accepted so the policy can become field-aware later;
    the MVP deliberately uses conservative intent matching and never sends the
    local record to a provider merely because a field is blank.
    """
    del artifact_context
    normalized = " ".join(question.lower().split())
    return any(term in normalized for term in CONNECTOR_INTENT_TERMS)


def is_trusted_url(url: str, extra_domains: set[str] | None = None) -> bool:
    try:
        hostname = (urlparse(url).hostname or "").lower().rstrip(".")
    except ValueError:
        return False

    if not hostname or urlparse(url).scheme not in {"http", "https"}:
        return False

    domains = DEFAULT_TRUSTED_DOMAINS | (extra_domains or set())

    if any(
        hostname == domain or hostname.endswith(f".{domain}")
        for domain in domains
    ):
        return True

    return hostname.endswith((".gov.sa", ".edu.sa", ".edu"))