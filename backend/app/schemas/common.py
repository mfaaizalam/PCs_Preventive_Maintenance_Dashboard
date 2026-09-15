from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, model_validator


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def _assume_utc_for_naive_datetimes(self):
        """
        SQLite drops tzinfo when reading DateTime(timezone=True)
        columns back, even though everything is written as UTC
        (datetime.now(timezone.utc)). Without this, the API sends
        timestamps with no 'Z'/offset, and the browser wrongly
        treats them as already-local time instead of converting -
        every timestamp ends up looking ~5 hours off in Pakistan.

        This stamps UTC back onto any naive datetime before it gets
        serialized, so the frontend can correctly convert to local
        time.
        """
        for name, value in self.__dict__.items():
            if isinstance(value, datetime) and value.tzinfo is None:
                setattr(self, name, value.replace(tzinfo=timezone.utc))
        return self


class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime