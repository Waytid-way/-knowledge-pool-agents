"""Application configuration loaded exclusively from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings shared by API, workers, and local tooling."""

    model_config = SettingsConfigDict(
        env_prefix="LLM_WIKI_",
        env_file=".env",
        extra="forbid",
    )

    database_url: str
    temporal_address: str
    s3_endpoint: str
    s3_bucket: str
    model_gateway_url: str
    environment: str = "development"
