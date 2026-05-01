from datetime import datetime
from typing import Optional

from pydantic import field_validator
from schemas.shared import TrimmedBaseModel
from utils.shared import validation_error


class NoteCreate(TrimmedBaseModel):
    text: Optional[str] = None
    user_id: Optional[int] = None
    month: int
    year: int

    @field_validator('month')
    def validate_month(cls, v):
        if v < 1 or v > 12:
            validation_error('month', 'Month must be between 1 and 12.', 'month')
        return v
    
    @field_validator('year')
    def validate_year(cls, v):
        if v < 1900 or v > 2100:
            validation_error('year', 'Year must be between 1900 and 2100.', 'year')
        return v


class NoteGet(TrimmedBaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None 
    user_id: Optional[int] = None


class NoteUpdate(TrimmedBaseModel):
    id: Optional[int] = None
    text: Optional[str] = None
    user_id: Optional[int] = None