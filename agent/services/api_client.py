"""
Pure HTTP layer between the agent and the central monitoring backend.

This module knows nothing about WMI, psutil, or the registry - it just
takes an already-built payload dict and tries to deliver it, with
retries. Collection/transformation logic lives in agent.py.
"""

import logging
import time

import requests

import config

logger = logging.getLogger("agent.api_client")


def send_report(payload: dict) -> dict | None:
    """
    POST a single agent report to the backend.

    Retries a few times on connection/timeout errors. If the backend
    is unreachable for this whole cycle, gives up cleanly - the next
    scheduled report in agent.py will simply try again in 60s.

    Returns the parsed JSON response (the updated Computer record) on
    success, or None on failure.
    """

    last_error = None

    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            response = requests.post(
                config.AGENT_REPORT_URL,
                json=payload,
                timeout=config.REQUEST_TIMEOUT_SECONDS,
            )

            if response.status_code == 422:
                logger.error(
                    "Backend rejected payload (validation error): %s",
                    response.text,
                )
                return None

            response.raise_for_status()

            logger.info(
                "Report sent successfully (attempt %d/%d)",
                attempt,
                config.MAX_RETRIES,
            )
            return response.json()

        except requests.exceptions.ConnectionError as exc:
            last_error = exc
            logger.warning(
                "Could not reach backend at %s (attempt %d/%d): %s",
                config.AGENT_REPORT_URL,
                attempt,
                config.MAX_RETRIES,
                exc,
            )

        except requests.exceptions.Timeout as exc:
            last_error = exc
            logger.warning(
                "Backend request timed out (attempt %d/%d): %s",
                attempt,
                config.MAX_RETRIES,
                exc,
            )

        except requests.exceptions.HTTPError as exc:
            logger.error("Backend returned an error status: %s", exc)
            return None

        if attempt < config.MAX_RETRIES:
            time.sleep(config.RETRY_BACKOFF_SECONDS)

    logger.error(
        "Giving up on this report after %d attempts: %s",
        config.MAX_RETRIES,
        last_error,
    )
    return None