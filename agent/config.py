import os

# ------------------------------------------------------------------
# BACKEND CONNECTION
# ------------------------------------------------------------------
API_BASE_URL = os.environ.get("AGENT_API_BASE_URL", "http://127.0.0.1:8000")
AGENT_REPORT_URL = f"{API_BASE_URL}/api/agent/report"

# ------------------------------------------------------------------
# REPORTING SCHEDULE
# ------------------------------------------------------------------
# Fast loop: cheap live metrics only (cpu/ram/disk/uptime).
FAST_REPORT_INTERVAL_SECONDS = 10

# Slow loop: heavy hardware/software/license/peripheral scan - this
# data barely changes, so it's only re-collected this often.
SLOW_REPORT_INTERVAL_SECONDS = 1800  # 30 minutes

# ------------------------------------------------------------------
# HTTP BEHAVIOUR
# ------------------------------------------------------------------
REQUEST_TIMEOUT_SECONDS = 15
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5

# ------------------------------------------------------------------
# AGENT IDENTITY
# ------------------------------------------------------------------
# Stored OUTSIDE the project folder so it can never end up in git and
# survives re-clones/re-deploys of the code on the same machine.
AGENT_ID_DIR = os.environ.get("AGENT_ID_DIR", r"C:\ProgramData\LabAgent")
AGENT_ID_FILE = os.path.join(AGENT_ID_DIR, "agent_id.txt")

# ------------------------------------------------------------------
# OPTIONAL LAB METADATA
# ------------------------------------------------------------------
LAB_NAME = os.environ.get("AGENT_LAB_NAME")
LAB_SECTION = os.environ.get("AGENT_LAB_SECTION")
ASSET_ID = os.environ.get("AGENT_ASSET_ID")