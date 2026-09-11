"""
Pure HTTP layer between the agent and the central monitoring backend.
"""

import logging
import time

import requests

import config

logger = logging.getLogger("agent.api_client")


def send_report(payload: dict) -> dict | None:
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


def send_shutdown_ack(agent_id: str) -> None:
    try:
        url = config.AGENT_SHUTDOWN_ACK_URL_TEMPLATE.format(agent_id=agent_id)
        requests.post(url, timeout=5)
    except requests.exceptions.RequestException as exc:
        logger.warning("Could not send shutdown ack (shutting down anyway): %s", exc)