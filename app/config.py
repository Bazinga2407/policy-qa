from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    OPENAI_API_KEY: str = Field(default="")
    EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")
    CHAT_MODEL: str = Field(default="gpt-4o-mini")
    STORAGE_DIR: str = Field(default="./storage")
    APP_SECRET: str = Field(default="dev-secret")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
Path(settings.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
