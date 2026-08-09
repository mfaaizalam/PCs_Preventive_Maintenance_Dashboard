from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class AuditLogBase(BaseModel):
    user_id: int | None = None
    action: str = Field(..., max_length=100)
    entity_type: str | None = Field(default=None, max_length=50)
    entity_id: str | None = Field(default=None, max_length=100)
    details: str | None = None
    ip_address: str | None = Field(default=None, max_length=45)


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogResponse(AuditLogBase, ORMModel):
    id: int
    created_at: datetime
