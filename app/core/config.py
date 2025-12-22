from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str
    ENV: str
    DATABASE_URL: str
    model_config = {"extra": "ignore", "env_file": ".env"}

settings = Settings()
