"""
Run this on a lab PC to point its agent at a new server IP.

Takes effect on the agent's NEXT report cycle (about 30 seconds) -
no restart, no reinstall.

Usage (Command Prompt, from the agent folder):
    python set_server_ip.py 192.168.1.50
    python set_server_ip.py 192.168.1.50 9000      (custom port, default 8000)

This just writes/updates server_config.json in the agent's data
folder (C:\\ProgramData\\LabAgent by default). You can also just edit
that JSON file directly with Notepad instead of running this script -
same effect.
"""
import json
import os
import sys

AGENT_ID_DIR = os.environ.get("AGENT_ID_DIR", r"C:\ProgramData\LabAgent")
SERVER_CONFIG_FILE = os.environ.get(
    "AGENT_SERVER_CONFIG_FILE",
    os.path.join(AGENT_ID_DIR, "server_config.json"),
)


def main():
    if len(sys.argv) < 2:
        print("Usage: python set_server_ip.py <server_ip> [port]")
        print(r"Example: python set_server_ip.py 192.168.1.50")
        sys.exit(1)

    ip = sys.argv[1].strip()
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000

    os.makedirs(AGENT_ID_DIR, exist_ok=True)
    with open(SERVER_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"server_ip": ip, "server_port": port}, f, indent=2)

    print(f"Saved. This agent will now report to: http://{ip}:{port}")
    print(f"File written: {SERVER_CONFIG_FILE}")
    print("Takes effect within ~30 seconds - no restart needed.")


if __name__ == "__main__":
    main()