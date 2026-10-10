from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["local", "test", "production"] = "local"
    log_level: str = "INFO"
    mysql_url: str = "mysql+pymysql://price_etl:change_me@localhost:3306/price_monitor?charset=utf8mb4"
    redis_url: str = "redis://localhost:6379/0"
    start_url: str = "https://books.toscrape.com/"
    download_delay: float = 2.0
    concurrent_requests: int = 2
    playwright_enabled: bool = False
    playwright_browser: str = "chromium"
    api_token: str = "change_this_service_token"
    alert_webhook_url: str | None = None
    report_dir: str = "reports"
    data_quality_score_threshold: float = Field(default=0.95, ge=0, le=1)


@lru_cache
def get_settings() -> Settings:
    return Settings()
