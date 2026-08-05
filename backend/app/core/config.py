from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_name: str = "Ruwi"
    app_env: str = "development"
    debug: bool = False
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    database_url: str = "sqlite+pysqlite:///./ruwi.db"
    jwt_secret: str = "development-only-change-me"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14
    max_image_mb: int = 10
    max_document_mb: int = 20
    local_storage_dir: str = "./storage"
    storage_provider: str = "local"
    ai_provider: str = "none"
    ai_api_key: str = ""
    vision_model: str = "gemini-2.5-flash"
    text_model: str = "gemini-2.5-flash"
    embedding_model: str = "text-embedding-004"
    tts_provider: str = "browser"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"
    demo_seed: bool = True
    demo_admin_email: str = "admin@example.com"
    demo_admin_password: str = "Admin123!"
    demo_curator_email: str = "curator@example.com"
    demo_curator_password: str = "Curator123!"
    demo_visitor_email: str = "visitor@example.com"
    demo_visitor_password: str = "Visitor123!"
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")
    @property
    def cors_list(self): return [x.strip() for x in self.cors_origins.split(",") if x.strip()]
@lru_cache
def get_settings(): return Settings()
settings=get_settings()
