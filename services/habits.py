

from models.habits import Habit
from schemas.habits import HabitCreate, HabitUpdate
from sqlalchemy.orm import Session, selectinload
from utils.shared import validation_error


def save_habit(payload: HabitCreate, db: Session):
    habit = Habit(**payload.dict())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def get_habits_by_user_id(user_id: int, db: Session):
    habits = db.query(Habit).options(selectinload(Habit.logs)).filter(Habit.user_id == user_id).all()
    return habits


def patch_habit(payload: HabitUpdate, db: Session):
    habit = db.query(Habit).filter(Habit.id == payload.id).first()

    if habit is None:
        validation_error("habit", "Habit not found.", "habit", 404)
    
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(habit, field, value)

    db.commit()
    db.refresh(habit)

    return habit


def remove_habit(id: int, db: Session):
    habit = db.query(Habit).filter(Habit.id == id).first()

    if habit is None:
        validation_error("habit", "Habit not found.", "habit", 404)

    db.delete(habit)
    db.commit()

    return True
