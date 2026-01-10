from datetime import datetime
from typing import Optional
from schemas.shared import TrimmedBaseModel


class NoteCreate(TrimmedBaseModel):
    text: Optional[str] = None
    user_id: Optional[int] = None


class NoteGet(TrimmedBaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None 
    user_id: Optional[int] = None


class NoteUpdate(TrimmedBaseModel):
    id: Optional[int] = None
    text: Optional[str] = None
    user_id: Optional[int] = None