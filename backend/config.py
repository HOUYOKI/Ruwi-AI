"""Environment-driven configuration for the Ruwi backend."""
import os

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")

ARTIFACTS_JSON_PATH = os.getenv("ARTIFACTS_JSON_PATH", "../data/artifacts.json")
ASSETS_DIR = os.getenv("ASSETS_DIR", "../assets/clean_artifacts")

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

CHAT_QUESTION_MAX_LENGTH = 2000
CLAUDE_REQUEST_TIMEOUT_SECONDS = 20.0
CLAUDE_MAX_RETRIES = 1
