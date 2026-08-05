from fastapi import HTTPException
from app.core.config import settings
class ProviderFactory:
    @staticmethod
    def ensure_configured():
        if settings.ai_provider=="none" or not settings.ai_api_key:
            raise HTTPException(503,detail={"code":"AI_PROVIDER_NOT_CONFIGURED","message":"Real AI analysis is not configured. Explore the clearly labeled demo experiences instead."})
        if settings.ai_provider not in {"gemini","openai"}:
            raise HTTPException(503,detail={"code":"AI_PROVIDER_UNSUPPORTED","message":"Configured AI provider is not supported"})
