

from models.habits import Habit
from schemas.habits import HabitCreate
from sqlalchemy.orm import Session


def save_habit(payload: HabitCreate, db: Session):
    habit = Habit(**payload.dict())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit