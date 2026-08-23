"""Environment-driven configuration for the Ruwi backend."""
import os

from dotenv import load_dotenv

load_dotenv()

# Provider-agnostic Narrator config. NARRATOR_PROVIDER names which
# {PROVIDER}_BASE_URL / {PROVIDER}_API_KEY pair to use (e.g. "glm" ->
# GLM_BASE_URL / GLM_API_KEY). No provider is hardcoded or defaulted here.
NARRATOR_PROVIDER = os.getenv("NARRATOR_PROVIDER")
NARRATOR_MODEL = os.getenv("NARRATOR_MODEL")
NARRATOR_TEMPERATURE = float(os.getenv("NARRATOR_TEMPERATURE", "0.5"))
NARRATOR_MAX_TOKENS = int(os.getenv("NARRATOR_MAX_TOKENS", "2048"))
EXPERIENCE_LLM_ENABLED = os.getenv("EXPERIENCE_LLM_ENABLED", "false").lower() in {"1", "true", "yes"}
VISION_PROVIDER = os.getenv("VISION_PROVIDER")
VISION_MODEL = os.getenv("VISION_MODEL")
VISION_TIMEOUT_SECONDS = float(os.getenv("VISION_TIMEOUT_SECONDS", "20"))
TTS_STABILITY = float(os.getenv("TTS_STABILITY", "0.21"))
TTS_STYLE = float(os.getenv("TTS_STYLE", "0.3"))
TTS_SIMILARITY_BOOST = float(os.getenv("TTS_SIMILARITY_BOOST", "0.75"))


def get_narrator_provider_credentials() -> tuple[str, str]:
    """Resolve (base_url, api_key) for NARRATOR_PROVIDER. Raises RuntimeError
    if NARRATOR_PROVIDER or its {PROVIDER}_BASE_URL/{PROVIDER}_API_KEY pair
    is missing."""
    if not NARRATOR_PROVIDER:
        raise RuntimeError("NARRATOR_PROVIDER environment variable is not set")
    prefix = NARRATOR_PROVIDER.upper()
    base_url = os.getenv(f"{prefix}_BASE_URL")
    api_key = os.getenv(f"{prefix}_API_KEY")
    if not base_url or not api_key:
        raise RuntimeError(
            f"NARRATOR_PROVIDER is '{NARRATOR_PROVIDER}' but missing "
            f"{prefix}_BASE_URL and/or {prefix}_API_KEY"
        )
    return base_url, api_key


def get_vision_provider_credentials() -> tuple[str, str]:
    """Resolve vision credentials independently from the Narrator provider."""
    base_url = os.getenv("VISION_BASE_URL")
    api_key = os.getenv("VISION_API_KEY")
    if base_url and api_key:
        return base_url, api_key
    if not VISION_PROVIDER:
        raise RuntimeError(
            "Vision is not configured. Set VISION_MODEL, VISION_BASE_URL, and VISION_API_KEY."
        )
    prefix = VISION_PROVIDER.upper()
    base_url = os.getenv(f"{prefix}_BASE_URL")
    api_key = os.getenv(f"{prefix}_API_KEY")
    if not base_url or not api_key:
        raise RuntimeError(
            f"VISION_PROVIDER is '{VISION_PROVIDER}' but missing "
            f"{prefix}_BASE_URL and/or {prefix}_API_KEY"
        )
    return base_url, api_key


def get_tts_credentials() -> tuple[str, str, str]:
    """Resolve (api_key, voice_id_en, voice_id_ar) for ElevenLabs TTS,
    lazily — mirrors get_narrator_provider_credentials(). Raises
    RuntimeError if ELEVENLABS_API_KEY is missing."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY environment variable is not set")
    voice_id_en = os.getenv("ELEVENLABS_VOICE_ID_EN", "")
    voice_id_ar = os.getenv("ELEVENLABS_VOICE_ID_AR", "")
    return api_key, voice_id_en, voice_id_ar


ARTIFACTS_JSON_PATH = os.getenv("ARTIFACTS_JSON_PATH", "../data/artifacts.json")
ASSETS_DIR = os.getenv("ASSETS_DIR", "../assets/clean_artifacts")

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

CHAT_QUESTION_MAX_LENGTH = 2000
def narrator_is_configured() -> bool:
    if not NARRATOR_PROVIDER or not NARRATOR_MODEL:
        return False
    prefix = NARRATOR_PROVIDER.upper()
    return bool(os.getenv(f"{prefix}_BASE_URL") and os.getenv(f"{prefix}_API_KEY"))


def vision_is_configured() -> bool:
    if not VISION_MODEL:
        return False
    if os.getenv("VISION_BASE_URL") and os.getenv("VISION_API_KEY"):
        return True
    if not VISION_PROVIDER:
        return False
    prefix = VISION_PROVIDER.upper()
    return bool(os.getenv(f"{prefix}_BASE_URL") and os.getenv(f"{prefix}_API_KEY"))


def tts_configuration_status() -> dict[str, bool]:
    return {
        "configured": bool(os.getenv("ELEVENLABS_API_KEY")),
        "english_voice": bool(os.getenv("ELEVENLABS_VOICE_ID_EN")),
        "arabic_voice": bool(os.getenv("ELEVENLABS_VOICE_ID_AR")),
    }


def provider_preflight() -> dict:
    """Return readiness booleans only; never expose credentials or provider URLs."""
    return {
        "core": {"collection": True, "curated_experiences": True},
        "narrator": {"configured": narrator_is_configured()},
        "vision": {"configured": vision_is_configured()},
        "tts": tts_configuration_status(),
    }
