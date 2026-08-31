from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_USERNAME: str = ""
    DB_PASSWORD: str = ""
    SECRET_KEY: str = ""
    DB_HOST: str = "localhost"
    DB_NAME: str = ""
    DB_PORT: int = 5432

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
