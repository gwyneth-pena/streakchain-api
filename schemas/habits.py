

from typing import Optional
from schemas.shared import TrimmedBaseModel
from utils.shared import validation_error
from pydantic import model_validator


class HabitCreate(TrimmedBaseModel):
    name: str
    frequency: int
    color: Optional[str] = None
    user_id: Optional[int] = None

    @model_validator(mode='after')
    def validate_fields(cls, values):
        frequency = values.frequency

        if frequency < 0 or frequency > 31:
            validation_error('frequency', 'Frequency must be between 0 and 31.', 'frequency')
        
        return values