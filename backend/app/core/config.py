from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FinPilot API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://finpilot:finpilot@localhost:5432/finpilot"
    jwt_secret: str = "replace-me-for-local-development"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173"
    admin_username: str = "admin"
    admin_password: str = "admin123"
    viewer_username: str = "viewer"
    viewer_password: str = "viewer123"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


settings = Settings()
