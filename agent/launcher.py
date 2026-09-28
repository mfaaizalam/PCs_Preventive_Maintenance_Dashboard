"""
Lab Monitoring Agent Launcher
=============================

This is the ONLY piece that runs continuously on a lab PC. It does not
collect or report any system data itself - it has one job: ask the
server "should monitoring be on right now?" and start/stop the real
agent (agent.exe) accordingly.

Why this exists: an IT Manager needs to be able to pause and resume
monitoring on every PC from the dashboard, with nobody visiting a PC in
person. Something has to stay resident to receive that "turn back on"
signal - a fully-exited process cannot be woken remotely by itself.
This launcher is that one small, clearly-named, disclosed piece; the
actual monitoring/collection code (agent.exe) is what genuinely stops
and starts.

During an audit, this is what shows up in Task Manager/Services -
nothing hidden, nothing else running. Its whole job is visible in this
file's logging: "starting monitoring agent" / "stopping monitoring
agent", nothing more.
"""

import logging
import os
import subprocess
import sys
import time
import uuid

import requests

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("agent.launcher")


def get_or_create_agent_id() -> str:
    """Same id file agent.py uses, so the launcher and the agent always agree
    on which computer they're talking about."""
    os.makedirs(config.AGENT_ID_DIR, exist_ok=True)
    try:
        with open(config.AGENT_ID_FILE, "r", encoding="utf-8") as f:
            existing = f.read().strip()
            if existing:
                return existing
    except FileNotFoundError:
        pass

    new_id = uuid.uuid4().hex
    with open(config.AGENT_ID_FILE, "w", encoding="utf-8") as f:
        f.write(new_id)
    return new_id


def check_status(agent_id: str) -> dict | None:
    """Returns the server's pause/resume flags, or None if the server
    couldn't be reached (in which case the launcher leaves things as they
    are this cycle rather than guessing)."""
    try:
        url = config.AGENT_PAUSE_STATUS_URL_TEMPLATE.format(agent_id=agent_id)
        response = requests.get(url, timeout=config.REQUEST_TIMEOUT_SECONDS)
        if response.status_code == 404:
            return {"pending_pause": False, "pending_resume": False, "monitoring_paused": False}
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        logger.warning("Could not reach server (%s) - leaving agent as-is this cycle", exc)
        return None


def send_ack(agent_id: str, kind: str) -> None:
    template = (
        config.AGENT_PAUSE_ACK_URL_TEMPLATE if kind == "pause"
        else config.AGENT_RESUME_ACK_URL_TEMPLATE
    )
    try:
        requests.post(template.format(agent_id=agent_id), timeout=5)
    except requests.exceptions.RequestException as exc:
        logger.warning("Could not send %s ack: %s", kind, exc)


def stop_agent(child: subprocess.Popen) -> None:
    child.terminate()
    try:
        child.wait(timeout=10)
    except subprocess.TimeoutExpired:
        child.kill()


def run_forever() -> None:
    agent_id = get_or_create_agent_id()
    logger.info(
        "Launcher watching agent_id=%s | agent exe=%s | checking every %ss",
        agent_id, config.AGENT_EXE_PATH, config.LAUNCHER_POLL_INTERVAL_SECONDS,
    )

    child: subprocess.Popen | None = None

    while True:
        status = check_status(agent_id)
        child_alive = child is not None and child.poll() is None

        if status is not None:
            if status.get("pending_pause"):
                if child_alive:
                    logger.info("Pause requested by dashboard - stopping monitoring agent")
                    stop_agent(child)
                    child = None
                send_ack(agent_id, "pause")

            elif status.get("pending_resume"):
                if not child_alive:
                    logger.info("Resume requested by dashboard - starting monitoring agent")
                    child = subprocess.Popen([config.AGENT_EXE_PATH])
                send_ack(agent_id, "resume")

            elif status.get("monitoring_paused"):
                if child_alive:  # shouldn't normally happen, but keep it honest
                    logger.info("Still marked paused - stopping monitoring agent")
                    stop_agent(child)
                    child = None

            else:
                if not child_alive:
                    logger.info("Normal operation - starting monitoring agent")
                    child = subprocess.Popen([config.AGENT_EXE_PATH])

        time.sleep(config.LAUNCHER_POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        run_forever()
    except KeyboardInterrupt:
        logger.info("Launcher stopped by user.")
        sys.exit(0)