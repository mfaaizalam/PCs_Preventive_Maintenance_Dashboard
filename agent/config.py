import os

API_BASE_URL = os.environ.get("AGENT_API_BASE_URL", "http://192.168.1.41:8000")
AGENT_REPORT_URL = f"{API_BASE_URL}/api/agent/report"

# Light report: CPU/RAM/disk usage + peripheral list/events (small payload).
FAST_REPORT_INTERVAL_SECONDS = int(os.environ.get("AGENT_FAST_INTERVAL", 30))

# Full report: installed software, licenses, RAM slots, storage devices.
# Sent once when the agent starts (and retried until the server accepts it),
# then every 3 hours.
SLOW_REPORT_INTERVAL_SECONDS = int(os.environ.get("AGENT_SLOW_INTERVAL", 3 * 60 * 60))

# When a full report has to be retried (server was down), re-use the inventory
# collected in the last N seconds instead of re-running the heavy collectors.
INVENTORY_CACHE_SECONDS = 300

REQUEST_TIMEOUT_SECONDS = 15
MAX_RETRIES = 3            # full report
LIGHT_MAX_RETRIES = 1      # 30s report: don't retry, the next cycle is only 30s away
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