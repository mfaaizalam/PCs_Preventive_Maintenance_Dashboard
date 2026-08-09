from datetime import date

from pydantic import BaseModel, Field

from app.models.enums import LicenseStatus, LicenseType
from app.schemas.common import ORMModel, TimestampSchema


class SoftwareLicenseBase(BaseModel):
    product_name: str = Field(..., max_length=200)
    vendor: str | None = Field(default=None, max_length=200)
    version: str | None = Field(default=None, max_length=100)
    license_type: LicenseType = LicenseType.UNKNOWN
    status: LicenseStatus = LicenseStatus.UNKNOWN
    expiry_date: date | None = None
    renewal_contact: str | None = Field(default=None, max_length=200)
    alert_schedule_days: str | None = Field(
        default="30,14,7,1",
        max_length=50,
        description="Comma-separated alert offsets in days",
    )
    is_activated: bool = False
    detected_automatically: bool = True
    notes: str | None = None


class SoftwareLicenseCreate(SoftwareLicenseBase):
    computer_id: int


class SoftwareLicenseUpsert(SoftwareLicenseBase):
    pass


class SoftwareLicenseUpdate(BaseModel):
    vendor: str | None = Field(default=None, max_length=200)
    version: str | None = Field(default=None, max_length=100)
    license_type: LicenseType | None = None
    status: LicenseStatus | None = None
    expiry_date: date | None = None
    renewal_contact: str | None = Field(default=None, max_length=200)
    alert_schedule_days: str | None = Field(default=None, max_length=50)
    is_activated: bool | None = None
    detected_automatically: bool | None = None
    notes: str | None = None


class SoftwareLicenseResponse(SoftwareLicenseBase, TimestampSchema, ORMModel):
    id: int
    computer_id: int
