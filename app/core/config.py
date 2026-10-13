from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Employee Management API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/employees"
    secret_key: str = "local-dev-secret-change-me"
    test_database_url: str = "sqlite+pysqlite:///:memory:"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
