from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./maintenance.db"

    # If a PC hasn't reported in this many seconds, the sweep marks
    # it offline. Should be a few multiples of the agent's fast report
    # interval (10s) to tolerate one or two missed/slow cycles.
    OFFLINE_THRESHOLD_SECONDS: int = 45

    # How often the background sweep checks for stale PCs.
    OFFLINE_SWEEP_INTERVAL_SECONDS: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()