"""Environment-driven configuration for the Ruwi backend."""
import os

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")

# Provider-agnostic Narrator config. NARRATOR_PROVIDER names which
# {PROVIDER}_BASE_URL / {PROVIDER}_API_KEY pair to use (e.g. "glm" ->
# GLM_BASE_URL / GLM_API_KEY). No provider is hardcoded or defaulted here.
NARRATOR_PROVIDER = os.getenv("NARRATOR_PROVIDER")
NARRATOR_MODEL = os.getenv("NARRATOR_MODEL")
NARRATOR_TEMPERATURE = float(os.getenv("NARRATOR_TEMPERATURE", "0.5"))
NARRATOR_MAX_TOKENS = int(os.getenv("NARRATOR_MAX_TOKENS", "2048"))
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
CLAUDE_REQUEST_TIMEOUT_SECONDS = 20.0
CLAUDE_MAX_RETRIES = 1
