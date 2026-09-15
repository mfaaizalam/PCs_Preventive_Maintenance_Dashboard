import os

API_BASE_URL = os.environ.get("AGENT_API_BASE_URL", "http://127.0.0.1:8000")
AGENT_REPORT_URL = f"{API_BASE_URL}/api/agent/report"

FAST_REPORT_INTERVAL_SECONDS = 10
SLOW_REPORT_INTERVAL_SECONDS = 1800  # 30 minutes

REQUEST_TIMEOUT_SECONDS = 15
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5

AGENT_ID_DIR = os.environ.get("AGENT_ID_DIR", r"C:\ProgramData\LabAgent")
AGENT_ID_FILE = os.path.join(AGENT_ID_DIR, "agent_id.txt")

# ------------------------------------------------------------------
# REMOTE SHUTDOWN 
# ------------------------------------------------------------------
AGENT_SHUTDOWN_ACK_URL_TEMPLATE = f"{API_BASE_URL}/api/agent/{{agent_id}}/shutdown-ack"
SHUTDOWN_GRACE_SECONDS = 5

LAB_NAME = os.environ.get("AGENT_LAB_NAME")
LAB_SECTION = os.environ.get("AGENT_LAB_SECTION")
ASSET_ID = os.environ.get("AGENT_ASSET_ID")