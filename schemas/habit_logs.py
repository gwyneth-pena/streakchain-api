
from typing import Optional
from schemas.shared import TrimmedBaseModel


class HabitLogCreate(TrimmedBaseModel):
    habit_id: int
    user_id: Optional[int] = None