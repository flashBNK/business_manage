from pathlib import Path

import yaml
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class _AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR.parent / "config" / ".env",
        env_prefix="APP_",
        extra="ignore",
    )

    name: str = "org_service"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    cors_origins: str = ""
    secret_key: SecretStr

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return env_settings, dotenv_settings, init_settings, file_secret_settings

    def get_cors_origins(self) -> list[str]:
        origins = [origin.strip().rstrip("/") for origin in self.cors_origins.split(",") if origin.strip()]
        if origins:
            return origins
        return ["*"] if self.debug else []


class _DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR.parent / "config" / ".env",
        env_prefix="DB_",
        extra="ignore",
    )

    user: str
    password: SecretStr
    host: str = "localhost"
    port: int = 5432
    name: str = "org_db"

    def get_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"
        )


class _JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR.parent / "config" / ".env",
        env_prefix="JWT_",
        extra="ignore",
    )

    public_key_path: Path = BASE_DIR.parent / "config" / "keys" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_lifetime: int = 15

    def get_public_key(self) -> str:
        return self.public_key_path.read_text()


class _KafkaSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR.parent / "config" / ".env", env_prefix="KAFKA_", extra="ignore"
    )

    bootstrap_servers: str = "localhost:9092"


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR.parent / "config" / ".env",
        extra="ignore",
    )
    app: _AppSettings
    database: _DatabaseSettings
    jwt: _JWTSettings
    kafka: _KafkaSettings

    @classmethod
    def load(cls) -> "_Settings":
        path = BASE_DIR.parent / "config" / "config.yaml"

        if not path.exists():
            raise FileNotFoundError(f"Could not find config.yaml in {path}")

        with open(path) as file:
            data = yaml.safe_load(file)

        return cls(
            app=_AppSettings(**data.get("app", {})),
            database=_DatabaseSettings(),
            jwt=_JWTSettings(),
            kafka=_KafkaSettings(),
        )


settings = _Settings.load()
