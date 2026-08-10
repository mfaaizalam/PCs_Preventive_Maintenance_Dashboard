import os

# ------------------------------------------------------------------
# BACKEND CONNECTION
# ------------------------------------------------------------------
# Point this at the LAN IP of the PC running the FastAPI backend.
# Every lab PC's agent sends its report here - do NOT leave this as
# 127.0.0.1 on any machine except the server itself.
API_BASE_URL = "http://127.0.0.1:8000"
AGENT_REPORT_URL = f"{API_BASE_URL}/api/agent/report"

# ------------------------------------------------------------------
# REPORTING SCHEDULE
# ------------------------------------------------------------------
REPORT_INTERVAL_SECONDS = 60

# ------------------------------------------------------------------
# HTTP BEHAVIOUR
# ------------------------------------------------------------------
REQUEST_TIMEOUT_SECONDS = 15
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5

# ------------------------------------------------------------------
# AGENT IDENTITY
# ------------------------------------------------------------------
# A stable, unique id is generated once per PC and cached here so the
# backend recognizes this machine on every future check-in (this is
# what makes the backend UPDATE the same row instead of creating a
# new computer every restart).
AGENT_ID_FILE = os.path.join(os.path.dirname(__file__), "agent_id.txt")

# ------------------------------------------------------------------
# OPTIONAL LAB METADATA
# ------------------------------------------------------------------
# Fill these in per deployment if useful, otherwise leave as None.
LAB_NAME = None
LAB_SECTION = None
ASSET_ID = None