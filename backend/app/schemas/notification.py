from datetime import datetime

from pydantic import BaseModel

from app.models.enums import PeripheralEventType


class HardwareEventBrief(BaseModel):
    """
    Small, card-friendly shape for a single hardware connect/disconnect
    event. Used to embed "recent hardware activity" directly on each
    computer in the dashboard overview (see ComputerSummaryResponse),
    so PC cards don't need a separate request per PC.
    """

    event_type: PeripheralEventType
    device_type: str | None = None
    message: str
    occurred_at: datetime


class HardwareNotificationResponse(BaseModel):
    """
    One row in the bell-icon notification feed: a hardware device that
    was removed (disconnected/missing), scoped to a specific computer.
    Built from the existing peripheral_events table joined against
    computers.hostname - no new table.
    """

    id: int
    computer_id: int
    agent_id: str
    hostname: str
    device_type: str | None = None
    message: str
    occurred_at: datetime