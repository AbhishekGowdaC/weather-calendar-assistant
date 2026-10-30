from datetime import date, time
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class EventRequest(BaseModel):
    location: str = Field(min_length=2, max_length=120)

    event_date: date

    start_time: time
    end_time: time

    event_type: Literal[
        "outdoor",
        "indoor",
        "mixed"
    ] = "outdoor"

    @model_validator(mode="after")
    def validate_event_time(self):
        if self.end_time <= self.start_time:
            raise ValueError(
                "End time must be later than start time."
            )

        if self.start_time.tzinfo or self.end_time.tzinfo:
            raise ValueError(
                "Provide local event times without timezone offsets."
            )

        return self