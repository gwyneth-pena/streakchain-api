from pydantic import field_validator
from datetime import datetime
from typing import Optional

from schemas.shared import TrimmedBaseModel
from utils.shared import validation_error

class HabitLogCreate(TrimmedBaseModel):
    habit_id: int
    log_date: str
    user_id: Optional[int] = None

    @field_validator("log_date")
    @classmethod
    def validate_log_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            validation_error(
                "log_date",
                "Log date must be in YYYY-MM-DD format and must be a valid date.",
                "log_date",
            )
        return v
    
