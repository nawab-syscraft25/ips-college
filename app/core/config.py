from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str
    ENV: str
    DATABASE_URL: str
    # Secret key used for session middleware. Override in .env for production.
    SECRET_KEY: str = "dev-secret-change-me"
    # Simple admin password (only for initial/dev use). Prefer real user management.
    ADMIN_PASSWORD: str = "admin"
    model_config = {"extra": "ignore", "env_file": ".env"}

settings = Settings()
