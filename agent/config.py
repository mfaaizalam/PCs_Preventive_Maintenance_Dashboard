import json
import os

# ------------------------------------------------------------------
# Directory where this agent stores its persistent identity + local
# runtime settings. Defined first because the server-IP block below
# stores its file here too.
# ------------------------------------------------------------------
AGENT_ID_DIR = os.environ.get("AGENT_ID_DIR", r"C:\ProgramData\LabAgent")
AGENT_ID_FILE = os.path.join(AGENT_ID_DIR, "agent_id.txt")

# ------------------------------------------------------------------
# ADDED: SERVER IP - CHANGEABLE WITHOUT REINSTALLING/RESTARTING THE AGENT
# ------------------------------------------------------------------
# All lab PCs use static IPs, but the IP of the PC running the backend
# server can still change (new PC, re-imaged NIC, etc). Before this
# change, API_BASE_URL was read from an environment variable ONCE when
# the process started - changing it meant editing the env var and
# restarting the agent (or the whole PC) for it to take effect.
#
# Now the agent re-reads the server address from a small local file
# on every report cycle (server_config.json, in AGENT_ID_DIR). So
# updating that file - by hand, by a remote script, or by
# `set_server_ip.py` (shipped alongside this file) - redirects an
# ALREADY-RUNNING agent to the new server within one report cycle
# (about 30s), no reinstall and no restart needed.
#
# File format (server_config.json):
#   { "server_ip": "192.168.1.50", "server_port": 8000 }
#
# If the file doesn't exist yet, this falls back to the
# AGENT_API_BASE_URL environment variable, and then to
# http://127.0.0.1:8000 - exactly the old default behaviour.
SERVER_CONFIG_FILE = os.environ.get(
    "AGENT_SERVER_CONFIG_FILE",
    os.path.join(AGENT_ID_DIR, "server_config.json"),
)

_env_default = os.environ.get("AGENT_API_BASE_URL", "http://127.0.0.1:8000")
_server_config_cache = {"mtime": None, "api_base_url": _env_default}


def _read_server_config_file():
    """Re-reads SERVER_CONFIG_FILE only when it changed on disk
    (checked via mtime), so this costs ~nothing on the hot path."""
    try:
        mtime = os.path.getmtime(SERVER_CONFIG_FILE)
    except OSError:
        # File doesn't exist (yet) - keep using env var / default.
        return _server_config_cache["api_base_url"]

    if mtime == _server_config_cache["mtime"]:
        return _server_config_cache["api_base_url"]

    try:
        with open(SERVER_CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        ip = str(data["server_ip"]).strip()
        port = int(data.get("server_port", 8000))
        base_url = f"http://{ip}:{port}"
    except Exception:
        # Malformed/half-written file - keep the last good value
        # instead of taking the agent offline over a typo.
        return _server_config_cache["api_base_url"]

    _server_config_cache["mtime"] = mtime
    _server_config_cache["api_base_url"] = base_url
    return base_url


def get_api_base_url():
    """Current backend base URL - re-checked against
    server_config.json every time it's called (cheap: one os.stat)."""
    return _read_server_config_file()


_URL_TEMPLATES = {
    "AGENT_REPORT_URL": "{base}/api/agent/report",
    "AGENT_SHUTDOWN_ACK_URL_TEMPLATE": "{base}/api/agent/{{agent_id}}/shutdown-ack",
    "AGENT_PAUSE_STATUS_URL_TEMPLATE": "{base}/api/agent/{{agent_id}}/pause-status",
    "AGENT_PAUSE_ACK_URL_TEMPLATE": "{base}/api/agent/{{agent_id}}/pause-ack",
    "AGENT_RESUME_ACK_URL_TEMPLATE": "{base}/api/agent/{{agent_id}}/resume-ack",
}


def __getattr__(name):
    """PEP 562 module-level dynamic attributes. agent.py, launcher.py
    and services/api_client.py all do `import config` and then read
    e.g. `config.AGENT_REPORT_URL` - this makes that same expression
    recompute from the CURRENT server IP every time it's read, instead
    of the IP that happened to be set when the process started. No
    other file needed to change."""
    if name == "API_BASE_URL":
        return get_api_base_url()
    if name in _URL_TEMPLATES:
        return _URL_TEMPLATES[name].format(base=get_api_base_url())
    raise AttributeError(f"module 'config' has no attribute {name!r}")


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

# ------------------------------------------------------------------
# REMOTE SHUTDOWN
# ------------------------------------------------------------------
SHUTDOWN_GRACE_SECONDS = 5

# ------------------------------------------------------------------
# LAUNCHER (the always-on process that starts/stops the real agent
# based on the pause/resume flag - see launcher.py). Nothing here
# collects or reports any data; it only starts/stops agent.exe.
# ------------------------------------------------------------------
LAUNCHER_POLL_INTERVAL_SECONDS = int(os.environ.get("LAUNCHER_POLL_INTERVAL", 30))
AGENT_EXE_PATH = os.environ.get(
    "AGENT_EXE_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent.exe"),
)

LAB_NAME = os.environ.get("AGENT_LAB_NAME")
LAB_SECTION = os.environ.get("AGENT_LAB_SECTION")
ASSET_ID = os.environ.get("AGENT_ASSET_ID")