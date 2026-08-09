from datetime import date

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel, TimestampSchema


class InstalledSoftwareBase(BaseModel):
    name: str = Field(..., max_length=200)
    publisher: str | None = Field(default=None, max_length=200)
    version: str | None = Field(default=None, max_length=100)
    install_date: date | None = None
    is_authorized: bool | None = None


class InstalledSoftwareCreate(InstalledSoftwareBase):
    computer_id: int


class InstalledSoftwareUpsert(InstalledSoftwareBase):
    pass


class InstalledSoftwareUpdate(BaseModel):
    version: str | None = Field(default=None, max_length=100)
    install_date: date | None = None
    is_authorized: bool | None = None


class InstalledSoftwareResponse(InstalledSoftwareBase, TimestampSchema, ORMModel):
    id: int
    computer_id: int
