from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import AlertSeverity, AlertType
from app.schemas.common import ORMModel


class AlertBase(BaseModel):
    computer_id: int | None = None
    alert_type: AlertType
    severity: AlertSeverity
    title: str = Field(..., max_length=200)
    message: str
    source: str | None = Field(default=None, max_length=100)


class AlertCreate(AlertBase):
    pass


class AlertAcknowledge(BaseModel):
    acknowledged_by_id: int


class AlertResponse(AlertBase, ORMModel):
    id: int
    is_acknowledged: bool
    acknowledged_by_id: int | None
    acknowledged_at: datetime | None
    created_at: datetime
    resolved_at: datetime | None


class AlertSummaryResponse(ORMModel):
    id: int
    computer_id: int | None
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    is_acknowledged: bool
    created_at: datetime
