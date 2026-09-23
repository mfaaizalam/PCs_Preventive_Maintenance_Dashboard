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
    # DATA RETENTION
    # ------------------------------------------------------------------

    # Resolved/acknowledged alerts are deleted after this many days.
    ALERT_RETENTION_DAYS: int = 3

    # USB/peripheral connect-disconnect audit trail.
    PERIPHERAL_EVENT_RETENTION_DAYS: int = 60

    # Hardware/software/network change audit trail.
    HARDWARE_CHANGE_LOG_RETENTION_DAYS: int = 180

    # How often the retention sweep runs.
    # 3600 seconds = 1 hour.
    RETENTION_SWEEP_INTERVAL_SECONDS: int = 3600

    # ------------------------------------------------------------------
    # MAINTENANCE LOG RETENTION REMINDER
    # ------------------------------------------------------------------

    # Start showing the maintenance-data deletion reminder
    # 30 days before the half-year purge.
    #
    # H1:
    #   Data is deleted on July 1.
    #   Reminder starts on June 1.
    #
    # H2:
    #   Data is deleted on January 1.
    #   Reminder starts on December 1.
    MAINTENANCE_LOG_REMINDER_DAYS: int = 30

    # After the reminder starts, show it again every 5 days.
    #
    # Example for July 1 deletion:
    # June 1  -> reminder
    # June 6  -> reminder
    # June 11 -> reminder
    # June 16 -> reminder
    # June 21 -> reminder
    # June 26 -> reminder
    # July 1  -> data is deleted
    MAINTENANCE_LOG_REMINDER_INTERVAL_DAYS: int = 5

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
