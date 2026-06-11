from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"
    CLAUDE_MODEL: str = "claude-sonnet-4-6"
    DATABASE_URL: str = "postgresql+asyncpg://pipeline:pipeline@localhost:5432/pipeline"
    REDIS_URL: str = "redis://localhost:6379/0"
    MINIO_ENDPOINT: str = "http://localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "pipeline-a"
    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
