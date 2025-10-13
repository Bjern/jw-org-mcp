"""Configuration management for JW.Org MCP Tool."""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    model_config = ConfigDict(env_prefix="JWORG_MCP_")

    # JW.Org URLs
    jworg_base_url: str = "https://www.jw.org"
    jworg_home_url: str = "https://www.jw.org/en/"
    wol_base_url: str = "https://wol.jw.org"

    # Cache settings
    cache_ttl_seconds: int = 900  # 15 minutes
    enable_cache: bool = True

    # Request settings
    request_timeout: int = 30
    max_retries: int = 3
    retry_backoff_factor: float = 0.5

    # Performance settings
    max_concurrent_requests: int = 100
    connection_pool_size: int = 100

    # Default search settings
    default_language: str = "E"
    default_search_limit: int = 10
    default_search_filter: str = "all"

    # Logging
    log_level: str = "INFO"


settings = Settings()
