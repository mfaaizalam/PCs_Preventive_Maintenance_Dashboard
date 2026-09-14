from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./maintenance.db"


    SECRET_KEY: str = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    # If a PC hasn't reported in this many seconds, the sweep marks
    # it offline. Should be a few multiples of the agent's fast report
    # interval (10s) to tolerate one or two missed/slow cycles.
    OFFLINE_THRESHOLD_SECONDS: int = 45

    # How often the background sweep checks for stale PCs.
    OFFLINE_SWEEP_INTERVAL_SECONDS: int = 5

    # ------------------------------------------------------------------
    # DATA RETENTION (keeps a free-tier Neon instance from filling up)
    # ------------------------------------------------------------------
    # A resolved/acknowledged alert (or one whose PC has been healthy
    # since) is deleted this many days after it was created. Ticket
    # ask: "alerts show for 3 days then erase."
    ALERT_RETENTION_DAYS: int = 3

    # USB/peripheral connect-disconnect audit trail - useful for a
    # week or two of "who unplugged what", not forever.
    PERIPHERAL_EVENT_RETENTION_DAYS: int = 60

    # Hardware/software/network change audit trail - kept longer than
    # peripheral events since it's lower-volume and more useful for
    # "when did this PC's CPU change" history.
    HARDWARE_CHANGE_LOG_RETENTION_DAYS: int = 180

    # How often the retention sweep runs. Once an hour is plenty -
    # this is cleanup, not anything time-critical.
    RETENTION_SWEEP_INTERVAL_SECONDS: int = 3600

    # ------------------------------------------------------------------
    # REMOTE SHUTDOWN
    # ------------------------------------------------------------------
    # How long an agent waits between receiving a shutdown instruction
    # (in its next report response) and the OS actually powering off.
    # Gives a person sitting at that PC a chance to see the Windows
    # warning and save their work, or an admin a window to cancel.
    SHUTDOWN_GRACE_SECONDS: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()