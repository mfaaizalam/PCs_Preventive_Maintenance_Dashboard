from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./maintenance.db"

    # How many days of metrics_history to keep. Rows older than this
    # are deleted automatically - the table always holds a rolling
    # window, never grows past this window's size.
    METRIC_HISTORY_RETENTION_DAYS: int = 30

    # How often the cleanup job checks for expired rows. Doesn't need
    # to be exact - every few hours keeps the table close enough to a
    # true 30-day window without adding real query load.
    METRIC_HISTORY_CLEANUP_INTERVAL_HOURS: int = 6

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()