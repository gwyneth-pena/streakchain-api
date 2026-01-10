from typing import Optional
from schemas.shared import TrimmedBaseModel


class NoteCreate(TrimmedBaseModel):
    text: Optional[str] = None
    user_id: Optional[int] = None