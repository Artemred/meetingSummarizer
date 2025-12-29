from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 1
    FILE_UPLOAD_DIR: str = "uploads"
    WHISPER_HOST: str = "localhost"
    WHISPER_PORT: int = 9090
    SUMMARIZATION_HOST: str = "localhost"
    SUMMARIZATION_PORT: int = 11434
    MODEL_NAME: str = "model7"


settings = Settings()
